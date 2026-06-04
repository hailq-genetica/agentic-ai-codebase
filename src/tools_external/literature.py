import os
import re
import time
from io import BytesIO
from urllib.parse import urljoin, urlparse
from typing import Any, Optional

import PyPDF2
import requests
from bs4 import BeautifulSoup
from googlesearch import search


# ---------------------------------------------------------------------------
# Literature blacklist (source-study exclusion)
# ---------------------------------------------------------------------------

def _normalize_literature_blacklist(blacklist: Any) -> Optional[dict]:
    """
    Normalize config literature_blacklist into a dict with keys:
    urls, dois, pmids, pmcids, title_contains (each a list of strings).
    Returns None if blacklist is empty/None.
    Config key "pmcid" (singular) or "pmcids" both accepted.
    """
    if not blacklist:
        return None
    if isinstance(blacklist, list):
        # Simple list: treat as title_contains substrings (e.g. paper titles or DOI/URL snippets); lower for case-insensitive match
        items = [str(x).strip().lower() for x in blacklist if x]
        if not items:
            return None
        return {"urls": [], "dois": [], "pmids": [], "pmcids": [], "title_contains": items}
    if isinstance(blacklist, dict):
        pmcid_raw = blacklist.get("pmcid") or blacklist.get("pmcids") or []
        if not isinstance(pmcid_raw, list):
            pmcid_raw = [pmcid_raw] if pmcid_raw else []
        out = {
            "urls": [str(x).strip().lower() for x in (blacklist.get("urls") or [])],
            "dois": [str(x).strip().lower() for x in (blacklist.get("dois") or [])],
            "pmids": [str(x).strip() for x in (blacklist.get("pmids") or [])],
            "pmcids": [str(x).strip().upper() for x in pmcid_raw if x],  # PMC11370330 style
            "title_contains": [str(x).strip().lower() for x in (blacklist.get("title_contains") or [])],
        }
        if not any(out.values()):
            return None
        return out
    return None


def _url_base_for_match(url: str) -> str:
    """Return URL without query string or fragment, for stable blacklist matching.
    URLs with ?tracking=... or #section still match when the base path is blacklisted.
    """
    parsed = urlparse(url.strip())
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.scheme else f"{parsed.path}"
    return base.rstrip("/").lower()


def _is_blacklisted_url(url: str, blacklist: Optional[dict]) -> bool:
    """Return True if url should be excluded (matches blacklist).
    Matching uses substring: query params (?...) and fragments (#...) do not prevent a match—
    e.g. https://doi.org/10.1234/paper?utm_source=twitter still matches blacklist entry doi.org/10.1234/paper.
    """
    if not blacklist or not url:
        return False
    url_lower = url.lower().strip()
    url_base = _url_base_for_match(url)
    for pattern in blacklist.get("urls") or []:
        if not pattern:
            continue
        pattern_lower = pattern.lower()
        if pattern_lower in url_lower or pattern_lower in url_base:
            return True
    for doi in blacklist.get("dois") or []:
        if doi and (doi.lower() in url_lower or doi.lower() in url_base):
            return True
    for pmcid in blacklist.get("pmcids") or []:
        if not pmcid:
            continue
        pmcid_upper = pmcid.strip().upper()
        pmcid_norm = pmcid_upper if pmcid_upper.startswith("PMC") else f"PMC{pmcid_upper}"
        pmcid_lower = pmcid_norm.lower()
        if pmcid_lower in url_lower or pmcid_lower in url_base:
            return True
    return False


def _is_blacklisted_paper(
    *,
    title: Optional[str] = None,
    doi: Optional[str] = None,
    pmid: Optional[str] = None,
    pmcid: Optional[str] = None,
    url: Optional[str] = None,
    blacklist: Optional[dict] = None,
) -> bool:
    """Return True if this paper/source should be excluded."""
    if not blacklist:
        return False
    if title:
        title_lower = title.lower()
        for sub in blacklist.get("title_contains") or []:
            if sub and sub.lower() in title_lower:
                return True
    if doi:
        doi_n = doi.strip().lower()
        for d in blacklist.get("dois") or []:
            if d:
                d_lower = d.strip().lower()
                if d_lower in doi_n or doi_n in d_lower:
                    return True
    if pmid:
        pmid_s = str(pmid).strip()
        for p in blacklist.get("pmids") or []:
            if p and p == pmid_s:
                return True
    if pmcid:
        raw = (pmcid or "").strip().upper()
        pmcid_norm = raw if raw.startswith("PMC") else f"PMC{raw}"
        for pc in blacklist.get("pmcids") or []:
            if not pc:
                continue
            pc_norm = pc.strip().upper() if pc.strip().upper().startswith("PMC") else f"PMC{pc.strip()}"
            if pc_norm == pmcid_norm:
                return True
    if url and _is_blacklisted_url(url, blacklist):
        return True
    return False


def fetch_supplementary_info_from_doi(doi: str, output_dir: str = "supplementary_info", literature_blacklist: Optional[dict] = None):
    """Fetches supplementary information for a paper given its DOI and returns a research log.

    Args:
        doi: The paper DOI.
        output_dir: Directory to save supplementary files.
        literature_blacklist: Optional blacklist (from config) to exclude source studies; if DOI is blacklisted, returns a short message instead of fetching.

    Returns:
        dict: A dictionary containing a research log and the downloaded file paths.

    """
    bl = _normalize_literature_blacklist(literature_blacklist)
    if bl and _is_blacklisted_paper(doi=doi, blacklist=bl):
        return "This DOI is excluded from retrieval (source study blacklist). Use other literature to answer."
    research_log = []
    research_log.append(f"Starting process for DOI: {doi}")

    # CrossRef API to resolve DOI to a publisher page
    crossref_url = f"https://doi.org/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(crossref_url, headers=headers)

    if response.status_code != 200:
        log_message = f"Failed to resolve DOI: {doi}. Status Code: {response.status_code}"
        research_log.append(log_message)
        return {"log": research_log, "files": []}

    publisher_url = response.url
    research_log.append(f"Resolved DOI to publisher page: {publisher_url}")

    # Fetch publisher page
    response = requests.get(publisher_url, headers=headers)
    if response.status_code != 200:
        log_message = f"Failed to access publisher page for DOI {doi}."
        research_log.append(log_message)
        return {"log": research_log, "files": []}

    # Parse page content
    soup = BeautifulSoup(response.content, "html.parser")
    supplementary_links = []

    # Look for supplementary materials by keywords or links
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        text = link.get_text().lower()
        if "supplementary" in text or "supplemental" in text or "appendix" in text:
            full_url = urljoin(publisher_url, href)
            supplementary_links.append(full_url)
            research_log.append(f"Found supplementary material link: {full_url}")

    if not supplementary_links:
        log_message = f"No supplementary materials found for DOI {doi}."
        research_log.append(log_message)
        return research_log

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    research_log.append(f"Created output directory: {output_dir}")

    # Download supplementary materials
    downloaded_files = []
    for link in supplementary_links:
        file_name = os.path.join(output_dir, link.split("/")[-1])
        file_response = requests.get(link, headers=headers)
        if file_response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(file_response.content)
            downloaded_files.append(file_name)
            research_log.append(f"Downloaded file: {file_name}")
        else:
            research_log.append(f"Failed to download file from {link}")

    if downloaded_files:
        research_log.append(f"Successfully downloaded {len(downloaded_files)} file(s).")
    else:
        research_log.append(f"No files could be downloaded for DOI {doi}.")

    return "\n".join(research_log)


def query_arxiv(query: str, max_papers: int = 10, literature_blacklist: Optional[dict] = None) -> str:
    """Query arXiv for papers based on the provided search query.

    Parameters
    ----------
    - query (str): The search query string.
    - max_papers (int): The maximum number of papers to retrieve (default: 10).
    - literature_blacklist: Optional blacklist to exclude source studies from results.

    Returns
    -------
    - str: The formatted search results or an error message.

    """
    import arxiv

    try:
        bl = _normalize_literature_blacklist(literature_blacklist)
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_papers, sort_by=arxiv.SortCriterion.Relevance)
        kept = []
        for paper in client.results(search):
            if bl and _is_blacklisted_paper(title=paper.title, url=getattr(paper, "entry_id", None) or getattr(paper, "pdf_url", ""), blacklist=bl):
                continue
            kept.append(f"Title: {paper.title}\nSummary: {paper.summary}")
        results = "\n\n".join(kept)
        return results if results else "No papers found on arXiv."
    except Exception as e:
        return f"Error querying arXiv: {e}"


def query_scholar(query: str, literature_blacklist: Optional[dict] = None) -> str:
    """Query Google Scholar for papers based on the provided search query.

    Parameters
    ----------
    - query (str): The search query string.
    - literature_blacklist: Optional blacklist to exclude source studies from results.

    Returns
    -------
    - str: The first search result formatted or an error message.

    """
    from scholarly import ProxyGenerator, scholarly

    bl = _normalize_literature_blacklist(literature_blacklist)
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    try:
        search_query = scholarly.search_pubs(query)
        for result in search_query:
            if not result:
                continue
            bib = result.get("bib") or {}
            title = bib.get("title") or ""
            pub_url = result.get("pub_url") or result.get("eprint_url") or ""
            if bl and _is_blacklisted_paper(title=title or None, url=pub_url or None, blacklist=bl):
                continue
            return f"Title: {bib['title']}\nYear: {bib['pub_year']}\nVenue: {bib['venue']}\nAbstract: {bib['abstract']}"
        return "No results found on Google Scholar."
    except Exception as e:
        return f"Error querying Google Scholar: {e}"


def query_pubmed(query: str, max_papers: int = 10, max_retries: int = 3, literature_blacklist: Optional[dict] = None) -> str:
    """Query PubMed for papers based on the provided search query.

    Parameters
    ----------
    - query (str): The search query string.
    - max_papers (int): The maximum number of papers to retrieve (default: 10).
    - max_retries (int): Maximum number of retry attempts with modified queries (default: 3).
    - literature_blacklist: Optional blacklist to exclude source studies from results (e.g. the paper that produced the dataset).

    Returns
    -------
    - str: The formatted search results or an error message.

    """
    from pymed import PubMed

    try:
        bl = _normalize_literature_blacklist(literature_blacklist)
        pubmed = PubMed(tool="MyTool", email="your-email@example.com")  # Update with a valid email address

        # Initial attempt
        papers = list(pubmed.query(query, max_results=max_papers))

        # Retry with modified queries if no results
        retries = 0
        while not papers and retries < max_retries:
            retries += 1
            # Simplify query with each retry by removing the last word
            simplified_query = " ".join(query.split()[:-retries]) if len(query.split()) > retries else query
            time.sleep(1)  # Add delay between requests
            papers = list(pubmed.query(simplified_query, max_results=max_papers))

        if papers:
            kept = []
            for paper in papers:
                pmid = getattr(paper, "pubmed_id", None) or getattr(paper, "pmid", None)
                if pmid and isinstance(pmid, list):
                    pmid = pmid[0] if pmid else None
                pmcid = getattr(paper, "pmc_id", None) or getattr(paper, "pmcid", None)
                if isinstance(pmcid, list):
                    pmcid = pmcid[0] if pmcid else None
                if bl and _is_blacklisted_paper(
                    title=getattr(paper, "title", None),
                    doi=getattr(paper, "doi", None),
                    pmid=pmid,
                    pmcid=pmcid,
                    blacklist=bl,
                ):
                    continue
                kept.append(f"Title: {paper.title}\nAbstract: {paper.abstract}\nJournal: {paper.journal}")
            results = "\n\n".join(kept)
            return results if results else "No papers found on PubMed after applying filters."
        else:
            return "No papers found on PubMed after multiple query attempts."
    except Exception as e:
        return f"Error querying PubMed: {e}"


def search_google(query: str, num_results: int = 3, language: str = "en", literature_blacklist: Optional[dict] = None) -> str:
    """Search using Google search.

    Args:
        query (str): The search query (e.g., "protocol text or seach question")
        num_results (int): Number of results to return (default: 10)
        language (str): Language code for search results (default: 'en')
        literature_blacklist: Optional blacklist to exclude URLs (e.g. source study links).

    Returns:
        str: Formatted search results (title, URL, description); blacklisted URLs are omitted.

    """
    try:
        bl = _normalize_literature_blacklist(literature_blacklist)
        results_string = ""
        search_query = f"{query}"

        print(f"Searching for {search_query} with {num_results} results and {language} language")

        for res in search(search_query, num_results=num_results, lang=language, advanced=True):
            url = getattr(res, "url", "") or ""
            title = getattr(res, "title", "") or ""
            if bl and (_is_blacklisted_url(url, bl) or _is_blacklisted_paper(title=title or None, url=url or None, blacklist=bl)):
                continue
            print(f"Found result: {title}")
            description = getattr(res, "description", "") or ""
            results_string += f"Title: {title}\nURL: {url}\nDescription: {description}\n\n"

    except Exception as e:
        print(f"Error performing search: {str(e)}")
    return results_string


def advanced_web_search_claude(
    query: str,
    max_searches: int = 1,
    max_retries: int = 3,
    literature_blacklist: Optional[dict] = None,
) -> str:
    """
    Initiate an advanced web search by launching a specialized agent to collect relevant information and citations through multiple rounds of web searches for a given query.
    Craft the query carefully for the search agent to find the most relevant information.

    Parameters
    ----------
    query : str
        The search phrase you want Claude to look up.
    max_searches : int, optional
        Upper-bound on searches Claude may issue inside this request.
    max_retries : int, optional
        Maximum number of retry attempts with exponential backoff.

    Returns
    -------
    str
        A formatted string containing the full text response from Claude and the non-blacklisted citations.
    """
    import random
    import anthropic

    # Use a valid model that supports web search
    model = "claude-sonnet-4-5-20250929"
    api_key = os.getenv("ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    bl = _normalize_literature_blacklist(literature_blacklist)
    tool_def = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_searches,
    }

    delay = random.randint(1, 10)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": query}],
                tools=[tool_def],
            )

            formatted_response = ""
            for blk in response.content:
                if blk.type == "text":
                    formatted_response += blk.text

                    # Append non-blacklisted citations, if any
                    if getattr(blk, "citations", None):
                        for cite in blk.citations:
                            url = getattr(cite, "url", "") or ""
                            title = getattr(cite, "title", "") or ""
                            if bl and _is_blacklisted_paper(title=title or None, url=url or None, blacklist=bl):
                                continue
                            formatted_response += f"(Citation: {title} - {url})"
            return formatted_response

        except Exception as e:
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            print(f"Error performing web search after {max_retries} attempts: {str(e)}")
            return f"Error performing web search after {max_retries} attempts: {str(e)}"


def extract_url_content(url: str, literature_blacklist: Optional[dict] = None) -> str:
    """Extract the text content of a webpage using requests and BeautifulSoup.

    Args:
        url: Webpage URL to extract content from
        literature_blacklist: Optional blacklist; if URL is blacklisted, returns a short message instead of content.

    Returns:
        Text content of the webpage

    """
    bl = _normalize_literature_blacklist(literature_blacklist)
    if bl and _is_blacklisted_url(url, bl):
        return "This URL is excluded from retrieval (source study blacklist). Use other sources to answer."
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    # Check if the response is in text format
    if "text/plain" in response.headers.get("Content-Type", "") or "application/json" in response.headers.get(
        "Content-Type", ""
    ):
        return response.text.strip()  # Return plain text or JSON response directly

    # If it's HTML, use BeautifulSoup to parse
    soup = BeautifulSoup(response.text, "html.parser")

    # Try to find main content first, fallback to body
    content = soup.find("main") or soup.find("article") or soup.body

    # Remove unwanted elements
    for element in content(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        element.decompose()

    # Extract text with better formatting
    paragraphs = content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])
    cleaned_text = []

    for p in paragraphs:
        text = p.get_text().strip()
        if text:  # Only add non-empty paragraphs
            cleaned_text.append(text)

    return "\n\n".join(cleaned_text)


def extract_pdf_content(url: str, literature_blacklist: Optional[dict] = None) -> str:
    """Extract the text content of a PDF file given its URL.

    Args:
        url: URL of the PDF file to extract text from
        literature_blacklist: Optional blacklist; if URL is blacklisted, returns a short message instead of content.

    Returns:
        The extracted text content from the PDF

    """
    bl = _normalize_literature_blacklist(literature_blacklist)
    if bl and _is_blacklisted_url(url, bl):
        return "This URL is excluded from retrieval (source study blacklist). Use other sources to answer."
    try:
        # Check if the URL ends with .pdf
        if not url.lower().endswith(".pdf"):
            # If not, try to find a PDF link on the page
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # Look for PDF links in the HTML content
                pdf_links = re.findall(r'href=[\'"]([^\'"]+\.pdf)[\'"]', response.text)
                if pdf_links:
                    # Use the first PDF link found
                    if not pdf_links[0].startswith("http"):
                        # Handle relative URLs
                        base_url = "/".join(url.split("/")[:3])
                        url = base_url + pdf_links[0] if pdf_links[0].startswith("/") else base_url + "/" + pdf_links[0]
                    else:
                        url = pdf_links[0]
                else:
                    return f"No PDF file found at {url}. Please provide a direct link to a PDF file."

        # Download the PDF
        response = requests.get(url, timeout=30)

        # Check if we actually got a PDF file (by checking content type or magic bytes)
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/pdf" not in content_type and not response.content.startswith(b"%PDF"):
            return f"The URL did not return a valid PDF file. Content type: {content_type}"

        pdf_file = BytesIO(response.content)

        # Try with PyPDF2 first
        try:
            text = ""
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")

        # Clean up the text
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return "The PDF file did not contain any extractable text. It may be an image-based PDF requiring OCR."

        return text

    except requests.exceptions.RequestException as e:
        return f"Error downloading PDF: {str(e)}"
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
