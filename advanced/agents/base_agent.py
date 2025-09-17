"""Base Agent class for all job search agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union, TypeVar, Generic
import asyncio
import time
from datetime import datetime
from pydantic import BaseModel, Field
from utils.logging_setup import get_logger, log_kv, instrument

T = TypeVar('T')

class AgentResponse(BaseModel, Generic[T]):
    """Standardized agent response model."""
    success: bool
    result: Optional[T] = None
    errors: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent(ABC):
    """Abstract base class for all agents in the job search system."""
    
    def __init__(self, name: str, config: Dict[str, Any], logger=None):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.name = name
        self.config = config
        self.logger = logger or get_logger(name)
        self.metrics = {
            'tasks_processed': 0,
            'tasks_successful': 0,
            'tasks_failed': 0,
            'total_processing_time': 0,
            'start_time': datetime.now()
        }
        
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """
        Process data specific to this agent.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed output data
        """
        pass
    
    async def execute(self, data: Any) -> Dict[str, Any]:
        """
        Execute the agent's task with error handling and metrics.
        
        Args:
            data: Input data to process
            
        Returns:
            Dictionary with result and metadata
        """
        start_time = time.time()
        self.metrics['tasks_processed'] += 1
        
        try:
            self.logger.info(f"{self.name} starting task processing")
            result = await self.process(data)
            
            self.metrics['tasks_successful'] += 1
            processing_time = time.time() - start_time
            self.metrics['total_processing_time'] += processing_time
            
            self.logger.info(f"{self.name} completed task in {processing_time:.2f}s")
            
            return {
                'success': True,
                'agent': self.name,
                'result': result,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.metrics['tasks_failed'] += 1
            processing_time = time.time() - start_time
            
            self.logger.error(f"{self.name} failed: {str(e)}")
            
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        runtime = (datetime.now() - self.metrics['start_time']).total_seconds()
        
        return {
            'agent_name': self.name,
            'tasks_processed': self.metrics['tasks_processed'],
            'tasks_successful': self.metrics['tasks_successful'],
            'tasks_failed': self.metrics['tasks_failed'],
            'success_rate': (self.metrics['tasks_successful'] / max(1, self.metrics['tasks_processed'])) * 100,
            'avg_processing_time': self.metrics['total_processing_time'] / max(1, self.metrics['tasks_processed']),
            'total_runtime_seconds': runtime,
            'uptime': f"{runtime / 3600:.2f} hours"
        }
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy and ready to process tasks."""
        return True
    
    def create_response(self, success: bool, data: Any = None, error: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a standardized response format for all agents.
        
        Args:
            success: Whether the operation was successful
            data: The main data payload (jobs, applications, etc.)
            error: Error message if failed
            metadata: Additional metadata about the operation
            
        Returns:
            Standardized response dictionary
        """
        response = {
            'success': success,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            response['data'] = data
            response['metadata'] = metadata or {}
        else:
            response['error'] = error or 'Unknown error'
            response['data'] = data  # May contain partial results
            
        return response
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


# Adapter function for backward compatibility during migration
def adapt_response(raw: Any) -> Dict[str, Any]:
    """
    Adapt raw responses to standardized format during migration.
    
    Args:
        raw: Raw response from agent
        
    Returns:
        Standardized response dictionary
    """
    if isinstance(raw, dict) and "success" in raw:
        return raw
    return {"success": True, "result": raw, "errors": [], "metrics": {}}