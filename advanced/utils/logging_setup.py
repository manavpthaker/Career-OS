"""Structured JSON logging setup for observability."""

import logging
import json
import sys
import time
from typing import Any, Dict, Optional
from functools import wraps

# Keys to redact from logs for security
REDACT_KEYS = {"api_key", "token", "email", "phone", "password", "secret", "credential"}


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""
    
    # Standard LogRecord attributes to exclude from custom fields
    EXCLUDE_ATTRS = {
        "msg", "args", "levelname", "levelno", "pathname", "filename", 
        "module", "exc_info", "exc_text", "stack_info", "lineno", 
        "funcName", "created", "msecs", "relativeCreated", "thread", 
        "threadName", "processName", "process", "name", "message",
        "asctime", "taskName", "extra"
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        base = {
            "t": int(time.time() * 1000),  # Timestamp in milliseconds
            "level": record.levelname,
            "msg": record.getMessage(),
            "event": getattr(record, "event", record.getMessage()),
            "logger": record.name,
        }
        
        # Merge any custom attributes from record.__dict__
        for key, value in record.__dict__.items():
            if key not in self.EXCLUDE_ATTRS:
                # Apply redaction for sensitive keys
                if key.lower() in REDACT_KEYS or any(r in key.lower() for r in REDACT_KEYS):
                    base[key] = "***REDACTED***"
                else:
                    base[key] = value
        
        # Also check record.extra if it exists (for backward compatibility)
        extra = getattr(record, "extra", {})
        if isinstance(extra, dict):
            for key, value in extra.items():
                if key not in base:  # Don't overwrite existing fields
                    if key.lower() in REDACT_KEYS or any(r in key.lower() for r in REDACT_KEYS):
                        base[key] = "***REDACTED***"
                    else:
                        base[key] = value
        
        return json.dumps(base, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with JSON formatting.
    
    Args:
        name: Logger name (e.g., "scraper", "enrichment")
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    
    # Configure logger
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False  # Don't propagate to root logger
    
    return logger


def log_kv(logger: logging.Logger, event: str, **kwargs):
    """
    Log structured key-value pairs.
    
    Args:
        logger: Logger instance
        event: Event name (e.g., "scraper.start")
        **kwargs: Key-value pairs to log
    """
    kwargs = dict(kwargs)
    kwargs.setdefault("event", event)
    
    # Extract run_id and trace_id if present
    run_id = kwargs.get('run_id')
    trace_id = kwargs.get('trace_id')
    
    # If we have a job_id but no trace_id, derive it
    if not trace_id and 'job_id' in kwargs:
        trace_id = kwargs['job_id'][:12]
        kwargs['trace_id'] = trace_id
    
    # Keep keys flat for easier indexing
    logger.info(event, extra=kwargs)


def instrument(stage_name: str):
    """
    Decorator to instrument agent methods with timing and error tracking.
    
    Args:
        stage_name: Name of the stage (e.g., "scrape", "enrich")
        
    Returns:
        Decorated function with instrumentation
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(self, payload: Any, *args, **kwargs):
            # Extract trace_id if available
            trace_id = None
            if isinstance(payload, dict):
                trace_id = payload.get('trace_id')
            
            # Start timing
            start_time = time.perf_counter()
            
            try:
                # Execute the function
                result = await fn(self, payload, *args, **kwargs)
                
                # Log success
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                log_kv(
                    self.logger, 
                    f"{stage_name}.success",
                    stage=stage_name,
                    trace_id=trace_id,
                    latency_ms=latency_ms
                )
                
                # Add metrics to result if it's a dict
                if isinstance(result, dict):
                    result.setdefault('metrics', {})
                    result['metrics']['latency_ms'] = latency_ms
                    result['metrics']['stage'] = stage_name
                    if trace_id:
                        result['metrics']['trace_id'] = trace_id
                
                return result
                
            except Exception as e:
                # Log error
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                log_kv(
                    self.logger,
                    f"{stage_name}.error",
                    stage=stage_name,
                    trace_id=trace_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    latency_ms=latency_ms
                )
                raise
        
        return wrapper
    return decorator


def log_pipeline_summary(
    logger: logging.Logger,
    run_id: str = None,
    trace_id: str = None,
    n_jobs: int = 0,
    n_applied: int = 0,
    total_ms: int = 0,
    error_count: int = 0,
    stage_metrics: Dict[str, int] = None
):
    """
    Log pipeline execution summary.
    
    Args:
        logger: Logger instance
        run_id: Pipeline run ID
        trace_id: Job trace ID (if single job)
        n_jobs: Number of jobs processed
        n_applied: Number of applications created
        total_ms: Total pipeline execution time
        error_count: Number of errors encountered
        stage_metrics: Per-stage timing metrics
    """
    kwargs = {
        "jobs": n_jobs,
        "applied": n_applied,
        "latency_ms": total_ms,
        "errors": error_count,
    }
    
    if run_id:
        kwargs["run_id"] = run_id
    if trace_id:
        kwargs["trace_id"] = trace_id
    
    # Backward compatibility: if trace_id but no run_id, use trace_id as run_id
    if trace_id and not run_id:
        kwargs["run_id"] = trace_id
    
    if stage_metrics:
        kwargs.update(stage_metrics)
    
    log_kv(logger, "pipeline.summary", **kwargs)


def log_safe_content(logger: logging.Logger, event: str, content: str, **kwargs):
    """
    Log content safely without PII.
    
    Args:
        logger: Logger instance
        event: Event name
        content: Content to log safely (will hash instead of logging raw)
        **kwargs: Additional key-value pairs
    """
    import hashlib
    
    content_hash = hashlib.sha1(content.encode()).hexdigest()[:8] if content else "empty"
    
    log_kv(
        logger,
        event,
        content_chars=len(content) if content else 0,
        content_sha1=content_hash,
        **kwargs
    )