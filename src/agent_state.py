"""Agent state management using dataclasses."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class TokenTracker:
    """Track cumulative token usage and context saturation.
    
    Tracks:
    - Input tokens (text + images combined, as reported by API)
    - Output tokens (reasoning + completion)
    - Image tokens (estimated, for separate tracking)
    - Cached tokens (if API reports them)
    - Context saturation (input_tokens / context_limit)
    """
    context_limit: int
    cumulative_input: int = 0
    cumulative_output: int = 0
    cumulative_reasoning: int = 0
    cumulative_completion: int = 0
    cumulative_image_tokens: int = 0  # Estimated image tokens sent
    cumulative_cached_tokens: int = 0  # Cached/reused tokens (if API reports)
    peak_saturation_pct: float = 0.0
    total_images_sent: int = 0  # Count of images sent to model
    
    def process_usage(self, usage, images_sent: int = 0) -> dict:
        """Process API usage and return token info dict. Updates cumulative counts.
        
        Args:
            usage: API response usage object
            images_sent: Number of images sent in this request (for estimation)
            
        Returns:
            dict with token breakdown for logging
        """
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        total_tokens = input_tokens + output_tokens
        
        # Extract input token details (cached tokens, etc.) if available
        input_details = getattr(usage, 'input_tokens_details', None)
        cached_tokens = 0
        if input_details:
            cached_tokens = getattr(input_details, 'cached_tokens', 0) or 0
        
        # Extract reasoning tokens (for reasoning models like o4-mini)
        output_details = getattr(usage, 'output_tokens_details', None)
        reasoning_tokens = 0
        if output_details:
            reasoning_tokens = getattr(output_details, 'reasoning_tokens', 0) or 0
        completion_tokens = output_tokens - reasoning_tokens
        
        # Estimate image tokens (API includes them in input_tokens, but we track separately)
        # Using ~765 tokens per image (high detail estimate for typical plots)
        from src.config import IMAGE_TOKENS_ESTIMATE
        image_tokens_estimate = images_sent * IMAGE_TOKENS_ESTIMATE.get("high", 765)
        
        # Update cumulative counts
        self.cumulative_input += input_tokens
        self.cumulative_output += output_tokens
        self.cumulative_reasoning += reasoning_tokens
        self.cumulative_completion += completion_tokens
        self.cumulative_image_tokens += image_tokens_estimate
        self.cumulative_cached_tokens += cached_tokens
        self.total_images_sent += images_sent
        
        # Context saturation is based on input tokens (which includes images)
        saturation_pct = (input_tokens / self.context_limit) * 100
        self.peak_saturation_pct = max(self.peak_saturation_pct, saturation_pct)
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "saturation_pct": saturation_pct,
            "cached_tokens": cached_tokens,
            "image_tokens_estimate": image_tokens_estimate,
            "images_sent": images_sent,
        }
    
    def format_log_line(self, token_info: dict) -> str:
        """Format a token usage log line with saturation bar."""
        saturation_pct = token_info["saturation_pct"]
        saturation_bar = "█" * int(saturation_pct / 10) + "░" * (10 - int(saturation_pct / 10))
        saturation_warning = " 🔴 CRITICAL" if saturation_pct > 95 else " ⚠️ HIGH" if saturation_pct > 80 else ""
        reasoning_info = f" (🧠 {token_info['reasoning_tokens']:,} reasoning + 💬 {token_info['completion_tokens']:,} completion)"
        
        # Add image info if images were sent
        image_info = ""
        if token_info.get("images_sent", 0) > 0:
            image_info = f" | 🖼️ {token_info['images_sent']} images (~{token_info['image_tokens_estimate']:,} tokens)"
        
        # Add cached token info if significant
        cached_info = ""
        if token_info.get("cached_tokens", 0) > 0:
            cached_info = f" | 💾 {token_info['cached_tokens']:,} cached"
        
        return f"📏 Tokens: {token_info['input_tokens']:,} in / {token_info['output_tokens']:,} out{reasoning_info}{image_info}{cached_info} | Context: [{saturation_bar}] {saturation_pct:.1f}%{saturation_warning}"


@dataclass
class AgentState:
    """Centralized agent execution state."""
    output_dir: Path
    task: str
    model: str
    context_limit: int
    client: Any = None  # LLMClient instance (unified interface for OpenAI/Anthropic)
    interactive: bool = False
    capture_telemetry: bool = True  # If False, skip pre_tool_call_hook (saves tokens)
    
    # Execution tracking
    step_count: int = 0
    plot_count: int = 0
    _next_plot_id: int = 0  # Monotonic counter — ensures unique filenames
    _next_exec_id: int = 0  # Monotonic counter for tool executions
    previous_response_id: Optional[str] = None
    adata_rna: Any = None   # scRNA-seq data (always RNA, or None)
    adata_atac: Any = None  # scATAC-seq data (always ATAC, or None)
    adata_atac_backed: Any = None  # scATAC-seq backed dataset (snapatac2, read-only)
    adata_combined: Any = None  # Joint/combined result — written by tools, not by data loading
    data_dir: Optional[Path] = None  # Auxiliary data folder (files accessible to tools/REPL)
    cnmf_usage_df: Any = None       # cNMF usage matrix (cells × programs)
    cnmf_spectra_scores_df: Any = None  # cNMF spectra scores (genes × programs)
    cnmf_top_genes_df: Any = None   # cNMF top genes per program
    
    # Literature blacklist: exclude source study (e.g. paper that produced the dataset) from search/fetch
    literature_blacklist: Optional[dict] = None  # From config: urls, dois, pmids, title_contains
    
    # History tracking - UNIFIED: each entry has tool info + token info together
    execution_history: list = field(default_factory=list)
    interaction_history: list = field(default_factory=list)
    conversation_log: list = field(default_factory=list)
    
    # Token tracking (cumulative counts only - per-step tokens are in execution_history)
    tokens: TokenTracker = field(default=None)
    
    def __post_init__(self):
        self.conversation_log = [f"[USER]: {self.task}"]
        self.tokens = TokenTracker(self.context_limit)
    
    def get_next_exec_id(self) -> int:
        """Get the next monotonic execution ID."""
        exec_id = self._next_exec_id
        self._next_exec_id += 1
        return exec_id
    
    def get_next_plot_id(self) -> int:
        """Get the next monotonic plot ID for unique filenames."""
        self._next_plot_id += 1
        self.plot_count += 1  # Also increment plot_count for state tracking
        return self._next_plot_id
    
    def get_recent_failures(self, tool_name: str, lookback: int = 5) -> list:
        """Get recent failures for a specific tool (for retry detection)."""
        return [h for h in self.execution_history[-lookback:] if h.get("name") == tool_name and not h.get("success")]
    
    def add_execution(self, name: str, args: dict, args_preview: str, intent: str,
                      reasoning_data: dict, success: bool, result_str: str,
                      token_info: dict = None, exec_id: int = None, error: str = None):
        """Record a complete execution entry (tool + tokens together)."""
        self.conversation_log.append(f"[TOOL CALL]: {name}({args_preview})")
        status = "✅" if success else "❌"
        self.conversation_log.append(f"[TOOL RESULT]: {status} {result_str[:200]}")
        
        record = {
            # Tool info
            "name": name, 
            "args": args, 
            "args_preview": args_preview,
            "intent": intent or "",
            "reasoning": reasoning_data or {},
            "success": success, 
            "step": self.step_count,
            "exec_id": exec_id,
            "error": error or "",
            # Token info (from API call that issued this tool)
            "input_tokens": token_info.get("input_tokens", 0) if token_info else 0,
            "output_tokens": token_info.get("output_tokens", 0) if token_info else 0,
            "reasoning_tokens": token_info.get("reasoning_tokens", 0) if token_info else 0,
            "completion_tokens": token_info.get("completion_tokens", 0) if token_info else 0,
            "saturation_pct": token_info.get("saturation_pct", 0) if token_info else 0,
            # Context
            "conversation": "\n".join(self.conversation_log)
        }
        self.execution_history.append(record)
    
    def add_reasoning(self, summary: str):
        """Record reasoning from model."""
        self.conversation_log.append(f"[REASONING]: {summary}")
    
    def add_feedback(self, text: str):
        """Record user feedback."""
        self.conversation_log.append(f"[USER FEEDBACK]: {text}")
        self.interaction_history.append({
            "step": self.step_count,
            "type": "feedback",
            "content": text,
            "response": "",
            "affects_context": True,
        })
        # Also add to execution_history for unified logging
        self.execution_history.append({
            "step": self.step_count,
            "exec_id": None,
            "name": "USER_FEEDBACK",
            "args_preview": text[:100],
            "success": True,
            "error": "",
            "input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
            "completion_tokens": 0, "saturation_pct": 0,
        })
    
    def add_question(self, question: str, answer: str):
        """Record user question and answer."""
        self.interaction_history.append({
            "step": self.step_count,
            "type": "question",
            "content": question,
            "response": answer[:500] if answer else "",
            "affects_context": False,
        })
        # Also add to execution_history for unified logging
        self.execution_history.append({
            "step": self.step_count,
            "exec_id": None,
            "name": "USER_QUESTION",
            "args_preview": question[:100],
            "success": True,
            "error": answer[:200] if answer else "",  # Store answer in error field for visibility
            "input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
            "completion_tokens": 0, "saturation_pct": 0,
        })
    
    def add_model_response(self, text: str, token_info: dict = None):
        """Record a final model text response (no tool call).
        
        This captures the model's concluding message so it appears
        in the wandb execution table alongside tool calls.
        """
        self.conversation_log.append(f"[MODEL RESPONSE]: {text[:500]}")
        self.execution_history.append({
            "step": self.step_count,
            "exec_id": None,
            "name": "MODEL_RESPONSE",
            "args_preview": text[:200],
            "success": True,
            "error": "",
            "input_tokens": token_info.get("input_tokens", 0) if token_info else 0,
            "output_tokens": token_info.get("output_tokens", 0) if token_info else 0,
            "reasoning_tokens": token_info.get("reasoning_tokens", 0) if token_info else 0,
            "completion_tokens": token_info.get("completion_tokens", 0) if token_info else 0,
            "saturation_pct": token_info.get("saturation_pct", 0) if token_info else 0,
        })
    