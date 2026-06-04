"""Logging utilities for the agent."""

import wandb


class AgentLogger:
    """Logger that writes to console, file, and optionally wandb."""
    
    def __init__(self):
        self._log_file = None
        self._wandb_run = None
    
    def set_log_file(self, file_handle):
        """Set the log file handle."""
        self._log_file = file_handle
    
    def set_wandb_run(self, run):
        """Set the wandb run reference."""
        self._wandb_run = run
    
    @property
    def wandb_run(self):
        """Get the wandb run reference."""
        return self._wandb_run
    
    def log(self, msg: str, wandb_log: dict = None):
        """Log to console, file, and optionally wandb.
        
        Args:
            msg: Message to print/write
            wandb_log: Optional dict of metrics to log to wandb
        """
        print(msg)
        if self._log_file:
            self._log_file.write(msg + "\n")
            self._log_file.flush()
        if self._wandb_run and wandb_log:
            wandb.log(wandb_log)
    
    def close(self):
        """Close the log file if open."""
        if self._log_file:
            self._log_file.close()
            self._log_file = None


# Global logger instance
logger = AgentLogger()


def log(msg: str, wandb_log: dict = None):
    """Convenience function to log using the global logger."""
    logger.log(msg, wandb_log)
