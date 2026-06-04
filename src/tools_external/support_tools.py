from __future__ import annotations

import importlib
import inspect
import os
import subprocess
import sys
from io import StringIO

import matplotlib.figure as mpl_figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.io as pio
import scanpy as sc
import seaborn as sns

_persistent_namespace = {'sc': sc, 'np': np, 'pd': pd, 'plt': plt, 'sns': sns, 'pio': pio}

# ---------------------------------------------------------------------------
# Plot tracking — paths of images saved during current REPL execution.
# Populated by monkey-patches on matplotlib/plotly save/show functions.
# Consumed by tool_executor after each REPL call for vision + wandb.
# ---------------------------------------------------------------------------

_repl_saved_plots: list[str] = []
_repl_saved_fignums: set[int] = set()
_repl_plot_counter = 0

_IMAGE_EXTENSIONS = frozenset({'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'})


def get_repl_saved_plots() -> list[str]:
    """Return and clear the list of image paths saved during REPL execution."""
    global _repl_saved_plots
    result = _repl_saved_plots.copy()
    _repl_saved_plots = []
    return result


def _is_image_path(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in _IMAGE_EXTENSIONS


def _get_figure_title(fig) -> str | None:
    """Extract a usable title from a matplotlib figure."""
    if fig._suptitle:
        t = fig._suptitle.get_text().strip()
        if t:
            return t
    if fig.axes:
        t = fig.axes[0].get_title().strip()
        if t:
            return t
    return None


def _save_remaining_figures(output_dir):
    """Save new unsaved matplotlib figures to disk and close all new figures.

    Figures already saved by savefig() or plt.show() patches (tracked in
    ``_repl_saved_fignums``) are just closed without re-saving.
    """
    global _repl_plot_counter
    new_fignums = set(plt.get_fignums()) - _repl_saved_fignums

    original_savefig = getattr(mpl_figure.Figure, "_original_savefig", mpl_figure.Figure.savefig)

    for fig_num in sorted(new_fignums):
        fig = plt.figure(fig_num)
        _repl_plot_counter += 1
        title = _get_figure_title(fig)
        if title:
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:50]
            filename = f"{safe}.png"
        else:
            filename = f"repl_figure_{_repl_plot_counter}.png"

        if output_dir:
            filepath = os.path.join(str(output_dir), filename)
            os.makedirs(str(output_dir), exist_ok=True)
        else:
            filepath = filename

        try:
            original_savefig(fig, filepath, dpi=150, bbox_inches="tight")
            _repl_saved_plots.append(filepath)
        except Exception:
            pass
        plt.close(fig)


# ---------------------------------------------------------------------------
# Read-only proxy for snapatac2 backed datasets
# ---------------------------------------------------------------------------

class _ReadOnlyMappingProxy:
    """Wraps a mapping-like attribute (.obs, .var, etc.) to block mutation."""

    def __init__(self, target):
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name):
        return getattr(self._target, name)

    def __getitem__(self, key):
        return self._target[key]

    def __setitem__(self, key, value):
        raise TypeError(
            "adata_atac_backed is READ-ONLY. Cannot assign to "
            f"'{key}'. Use the in-memory adata_atac instead, or create a copy."
        )

    def __delitem__(self, key):
        raise TypeError(
            "adata_atac_backed is READ-ONLY. Cannot delete "
            f"'{key}'. Use the in-memory adata_atac instead, or create a copy."
        )

    def __contains__(self, key):
        return key in self._target

    def __iter__(self):
        return iter(self._target)

    def __len__(self):
        return len(self._target)

    def __repr__(self):
        return repr(self._target)


class ReadOnlyAnnDataProxy:
    """Proxy that allows reads on a snapatac2 backed dataset but raises a clean
    Python error on any mutation attempt, preventing Rust panics / SIGABRT."""

    _MAPPING_ATTRS = frozenset({"obs", "var", "obsm", "varm", "obsp", "varp", "uns", "layers"})

    def __init__(self, backed):
        object.__setattr__(self, "_backed", backed)

    def __getattr__(self, name):
        val = getattr(self._backed, name)
        if name in self._MAPPING_ATTRS:
            return _ReadOnlyMappingProxy(val)
        return val

    def __setattr__(self, name, value):
        raise AttributeError(
            f"adata_atac_backed is READ-ONLY. Cannot set '.{name}'. "
            "Use the in-memory adata_atac instead, or create a copy."
        )

    def __repr__(self):
        return f"ReadOnlyProxy({self._backed!r})"


# ---------------------------------------------------------------------------
# Python REPL
# ---------------------------------------------------------------------------

def run_python_repl(command: str, adata_rna=None, adata_atac=None,
                    adata_atac_backed=None, adata_combined=None,
                    output_dir=None, data_dir=None,
                    usage_df=None, spectra_scores_df=None, top_genes_df=None) -> str:
    """Executes the provided Python command in a persistent environment and returns the output.
    Pre-loaded data objects (injected from agent state, not user-supplied):
      adata_rna  — scRNA-seq AnnData
      adata_atac — scATAC-seq AnnData
      adata_atac_backed — scATAC-seq backed dataset (snapatac2, read-only)
      adata_combined — joint/multimodal AnnData (if produced by a multimodal tool)
      data_dir — path (str) to auxiliary data folder with extra files
      output_dir — path (str) to output directory for plots
      usage_df — cNMF usage matrix (cells × programs), if loaded
      spectra_scores_df — cNMF spectra scores (genes × programs), if loaded
      top_genes_df — cNMF top genes per program, if loaded
    Variables defined in one execution persist across subsequent calls."""

    global _repl_saved_plots, _repl_saved_fignums
    _repl_saved_plots = []
    _repl_saved_fignums = set()

    command = command.strip("```").strip()

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    if adata_rna is not None:
        _persistent_namespace['adata_rna'] = adata_rna
    if adata_atac is not None:
        _persistent_namespace['adata_atac'] = adata_atac
    if adata_atac_backed is not None:
        _persistent_namespace['adata_atac_backed'] = adata_atac_backed
    if adata_combined is not None:
        _persistent_namespace['adata_combined'] = adata_combined
    if data_dir is not None:
        _persistent_namespace['data_dir'] = data_dir
    if usage_df is not None:
        _persistent_namespace['usage_df'] = usage_df
    if spectra_scores_df is not None:
        _persistent_namespace['spectra_scores_df'] = spectra_scores_df
    if top_genes_df is not None:
        _persistent_namespace['top_genes_df'] = top_genes_df

    if output_dir is not None:
        sc.settings.figdir = str(output_dir)

    try:
        _apply_plot_patches(output_dir)
        exec(command, _persistent_namespace)
        output = mystdout.getvalue()
    except BaseException as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        output = f"Error: {type(e).__name__}: {str(e)}"
    finally:
        sys.stdout = old_stdout

    # Save any new matplotlib figures the code left open (not already saved/shown)
    # and close them so _save_new_figures in tool_executor doesn't double-count.
    _save_remaining_figures(output_dir)

    return output


def _apply_plot_patches(output_dir=None):
    """Monkey-patch matplotlib and plotly save functions to redirect to output_dir.

    - matplotlib: patches Figure.savefig (covers fig.savefig and plt.savefig).
      Seaborn grid .savefig() methods delegate to Figure.savefig, so they are
      covered automatically.
    - plotly: patches pio.write_image and pio.write_html (covers fig.write_image
      and fig.write_html since those delegate to pio).
    """
    _apply_matplotlib_patches(output_dir)
    _apply_plotly_patches(output_dir)


def _apply_matplotlib_patches(output_dir=None):
    if not hasattr(mpl_figure.Figure, "_original_savefig"):
        mpl_figure.Figure._original_savefig = mpl_figure.Figure.savefig
    if not hasattr(plt, "_original_show"):
        plt._original_show = plt.show

    original_fig_savefig = mpl_figure.Figure._original_savefig

    def fig_savefig_with_redirect(self, *args, **kwargs):
        filename = args[0] if args else kwargs.get("fname", "unknown")
        if output_dir is not None and isinstance(filename, str) and not os.path.isabs(filename):
            new_filename = os.path.join(str(output_dir), os.path.basename(filename))
            os.makedirs(str(output_dir), exist_ok=True)
            if args:
                args = (new_filename,) + args[1:]
            else:
                kwargs["fname"] = new_filename
            filename = new_filename
        result = original_fig_savefig(self, *args, **kwargs)
        if isinstance(filename, str):
            print(f"Plot saved to: {filename}")
            if _is_image_path(filename):
                _repl_saved_plots.append(filename)
                _repl_saved_fignums.add(self.number)
        return result

    def patched_show(*args, **kwargs):
        global _repl_plot_counter
        for fig_num in plt.get_fignums():
            fig = plt.figure(fig_num)
            if fig_num not in _repl_saved_fignums:
                _repl_plot_counter += 1
                title = _get_figure_title(fig)
                if title:
                    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:50]
                    filename = f"{safe}.png"
                else:
                    filename = f"repl_show_{_repl_plot_counter}.png"

                if output_dir:
                    filepath = os.path.join(str(output_dir), filename)
                    os.makedirs(str(output_dir), exist_ok=True)
                else:
                    filepath = filename

                try:
                    original_fig_savefig(fig, filepath, dpi=150, bbox_inches="tight")
                    print(f"Plot saved to: {filepath}")
                    _repl_saved_plots.append(filepath)
                except Exception:
                    pass
            plt.close(fig)

    mpl_figure.Figure.savefig = fig_savefig_with_redirect
    plt.show = patched_show


def _apply_plotly_patches(output_dir=None):
    if not hasattr(pio, "_original_write_image"):
        pio._original_write_image = pio.write_image
    if not hasattr(pio, "_original_write_html"):
        pio._original_write_html = pio.write_html
    if not hasattr(pio, "_original_show"):
        pio._original_show = pio.show

    original_write_image = pio._original_write_image
    original_write_html = pio._original_write_html

    def _redirect_path(file):
        if output_dir is not None and isinstance(file, str) and not os.path.isabs(file):
            os.makedirs(str(output_dir), exist_ok=True)
            return os.path.join(str(output_dir), os.path.basename(file))
        return file

    def write_image_with_redirect(fig, file, *args, **kwargs):
        file = _redirect_path(file)
        result = original_write_image(fig, file, *args, **kwargs)
        if isinstance(file, str):
            print(f"Plot saved to: {file}")
            if _is_image_path(file):
                _repl_saved_plots.append(file)
        return result

    def write_html_with_redirect(fig, file, *args, **kwargs):
        file = _redirect_path(file)
        result = original_write_html(fig, file, *args, **kwargs)
        if isinstance(file, str):
            print(f"Plot saved to: {file}")
        return result

    def patched_plotly_show(fig, *args, **kwargs):
        """Save plotly figure to disk on fig.show() (no browser in agent context)."""
        global _repl_plot_counter
        _repl_plot_counter += 1
        filename = f"plotly_figure_{_repl_plot_counter}.png"
        filepath = _redirect_path(filename)
        try:
            original_write_image(fig, filepath)
            print(f"Plot saved to: {filepath}")
            _repl_saved_plots.append(filepath)
        except Exception:
            html_path = os.path.splitext(filepath)[0] + ".html"
            try:
                original_write_html(fig, html_path)
                print(f"Plot saved to: {html_path} (install kaleido for PNG export)")
            except Exception:
                print("Warning: Could not save plotly figure (install kaleido for image export)")

    pio.write_image = write_image_with_redirect
    pio.write_html = write_html_with_redirect
    pio.show = patched_plotly_show


# ---------------------------------------------------------------------------
# Utility tools
# ---------------------------------------------------------------------------

def read_function_source_code(function_name: str) -> str:
    """Read the source code of a function from a fully qualified module path."""
    parts = function_name.split(".")
    module_path = ".".join(parts[:-1])
    func_name = parts[-1]
    try:
        module = importlib.import_module(module_path)
        function = getattr(module, func_name)
        return inspect.getsource(function)
    except (ImportError, AttributeError) as e:
        return f"Error: Could not find function '{function_name}'. Details: {str(e)}"


def run_terminal(
    command: str,
    cwd: str | None = None,
    timeout: int = 120,
) -> str:
    """Run a shell command and return stdout, stderr, and exit code.

    Use this to run terminal commands such as: pip install, apt-get, curl, git,
    or any other shell command. Commands run in the current working directory
    unless cwd is provided. Avoid interactive prompts (e.g. use pip install -y
    or non-interactive flags where available).

    Parameters
    ----------
    command : str
        The shell command to run (e.g. "pip install scanpy", "ls -la").
    cwd : str, optional
        Working directory for the command. If None, uses the process cwd.
    timeout : int, default 120
        Timeout in seconds. The command is killed if it runs longer.

    Returns
    -------
    str
        Combined output: stdout and stderr, plus exit code. On timeout or
        failure, includes an error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        lines = []
        if out:
            lines.append("stdout:")
            lines.append(out)
        if err:
            lines.append("stderr:")
            lines.append(err)
        lines.append(f"exit_code: {result.returncode}")
        return "\n".join(lines)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def download_synapse_data(
    entity_ids: str | list[str],
    download_location: str = ".",
    follow_link: bool = False,
    recursive: bool = False,
    timeout: int = 300,
    entity_type: str = "dataset",
):
    """Download data from Synapse using entity IDs.

    Uses the synapse CLI to download files, folders, or projects from Synapse.
    Requires SYNAPSE_AUTH_TOKEN environment variable for authentication.
    Automatically installs synapseclient if not available.

    CRITICAL: Always check entity type from query_synapse() search results or user hints and pass the correct entity_type!
    The default entity_type="dataset" may not be appropriate for your entity.

    IMPORTANT: Multiple entity IDs are only supported for entity_type="file".
    For datasets, folders, and projects, only a single entity_id is supported.

    Parameters
    ----------
    entity_ids : str or list of str
        Synapse entity ID(s) to download.
        - For files: Can be a single ID string or list of ID strings
        - For datasets/folders/projects: Must be a single ID string only
    download_location : str, default "."
        Directory where files will be downloaded (current directory by default)
    follow_link : bool, default False
        Whether to follow links to download the linked entity
    recursive : bool, default False
        Whether to recursively download folders and their contents
        ONLY valid for entity_type="folder" - ignored for other types
    timeout : int, default 300
        Timeout in seconds for each download operation
    entity_type : str, default "dataset"
        Type of Synapse entity ("dataset", "file", "folder", "project")
        MUST match the actual entity type from search results or user hints!
        The default "dataset" should only be used for actual datasets.
        Check the 'node_type' field in search results to determine correct type.

    Returns
    -------
    dict
        Dictionary containing download results and any errors

    Notes
    -----
    Requires SYNAPSE_AUTH_TOKEN environment variable with your Synapse personal
    access token for authentication.

    AGENT USAGE GUIDANCE:
    1. Always check the 'node_type' field from query_synapse() search results or user hints
    2. Pass the correct entity_type parameter matching the node_type
    3. Do NOT rely on the default entity_type="dataset" unless confirmed
    4. For multiple downloads, ensure all entities are of type "file"
    5. Only use recursive=True with entity_type="folder"

    Examples
    --------
    # After searching with query_synapse(), check node_type and use appropriate entity_type:

    # If search result shows 'node_type': 'dataset'
    download_synapse_data("syn123456", entity_type="dataset")

    # If search result shows 'node_type': 'file'
    download_synapse_data("syn654321", entity_type="file")

    # If search result shows 'node_type': 'folder'
    download_synapse_data("syn789012", entity_type="folder", recursive=True)

    # Multiple files (only if all are 'node_type': 'file')
    download_synapse_data(["syn111", "syn222"], entity_type="file")
    """
    # Check for required authentication token
    synapse_token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not synapse_token:
        return {
            "success": False,
            "error": "SYNAPSE_AUTH_TOKEN environment variable is required for downloading",
            "suggestion": "Set SYNAPSE_AUTH_TOKEN with your Synapse personal access token",
        }

    # Check if synapse CLI is available
    try:
        subprocess.run(["synapse", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try to install synapseclient
            print("Installing synapseclient...")
            subprocess.run(["pip", "install", "synapseclient"], check=True)
            print("✓ synapseclient installed successfully")
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to install synapseclient: {e}",
                "suggestion": "Please install manually: pip install synapseclient",
            }

    # Ensure entity_ids is a list
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    # Validate that multiple IDs are only used with file entity type
    if len(entity_ids) > 1 and entity_type != "file":
        return {
            "success": False,
            "error": f"Multiple entity IDs are only supported for entity_type='file'. "
            f"For entity_type='{entity_type}', only a single entity_id is supported.",
            "suggestion": "Use a single entity_id string instead of a list, or change entity_type to 'file'",
        }

    # Validate that recursive is only used with folder entity type
    if recursive and entity_type != "folder":
        return {
            "success": False,
            "error": f"recursive=True is only valid for entity_type='folder'. "
            f"For entity_type='{entity_type}', recursive should be False.",
            "suggestion": "Set recursive=False, or change entity_type to 'folder' if appropriate",
        }

    # Create download directory if it doesn't exist
    os.makedirs(download_location, exist_ok=True)

    results = []
    errors = []

    for entity_id in entity_ids:
        try:
            # Build synapse download command with authentication
            if entity_type == "dataset":
                # For datasets, use query syntax to download the actual files
                cmd = [
                    "synapse",
                    "-p",
                    synapse_token,
                    "get",
                    "-q",
                    f"select * from {entity_id}",
                    "--downloadLocation",
                    download_location,
                ]
            else:
                # For files, folders, projects, use direct ID
                cmd = ["synapse", "-p", synapse_token, "get", entity_id, "--downloadLocation", download_location]

            # Add recursive flag only for folders (validation above ensures recursive is only True for folders)
            if entity_type == "folder" and recursive:
                cmd.append("-r")

            if follow_link:
                cmd.append("--followLink")

            # Execute download
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)

            results.append(
                {
                    "entity_id": entity_id,
                    "success": True,
                    "stdout": result.stdout,
                    "download_location": download_location,
                }
            )

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to download {entity_id}: {e.stderr if e.stderr else str(e)}"
            errors.append(error_msg)
            results.append({"entity_id": entity_id, "success": False, "error": error_msg})
        except subprocess.TimeoutExpired:
            error_msg = f"Download timeout for {entity_id} (>{timeout} seconds)"
            errors.append(error_msg)
            results.append({"entity_id": entity_id, "success": False, "error": error_msg})

    # Summary
    successful_downloads = [r for r in results if r["success"]]
    failed_downloads = [r for r in results if not r["success"]]

    return {
        "success": len(failed_downloads) == 0,
        "total_requested": len(entity_ids),
        "successful": len(successful_downloads),
        "failed": len(failed_downloads),
        "download_location": download_location,
        "results": results,
        "errors": errors if errors else None,
    }
