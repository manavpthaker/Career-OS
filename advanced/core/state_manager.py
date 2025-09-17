"""State management for workflow execution."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from utils import get_logger

logger = get_logger("state_manager")


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    INITIATED = "initiated"
    RESEARCHING = "researching"
    SCORING = "scoring"
    POSITIONING = "positioning"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class WorkflowState:
    """State of a workflow execution."""
    job_id: str
    job_url: str
    company: str
    role: str
    status: WorkflowStatus
    workflow_type: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Agent outputs
    research_data: Optional[Dict[str, Any]] = None
    scoring_result: Optional[Dict[str, Any]] = None
    positioning_strategy: Optional[Dict[str, Any]] = None
    generated_content: Optional[Dict[str, Any]] = None
    qa_result: Optional[Dict[str, Any]] = None

    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create state from dictionary."""
        data['status'] = WorkflowStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class StateManager:
    """Manages workflow state and persistence."""

    def __init__(self, state_dir: str = "data/state"):
        """Initialize the state manager.

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.active_states: Dict[str, WorkflowState] = {}

    def create_state(self,
                    job_id: str,
                    job_url: str,
                    company: str,
                    role: str,
                    workflow_type: str) -> WorkflowState:
        """Create a new workflow state.

        Args:
            job_id: Unique job identifier
            job_url: URL of the job posting
            company: Company name
            role: Role title
            workflow_type: Type of workflow to execute

        Returns:
            New workflow state
        """
        state = WorkflowState(
            job_id=job_id,
            job_url=job_url,
            company=company,
            role=role,
            status=WorkflowStatus.INITIATED,
            workflow_type=workflow_type
        )

        self.active_states[job_id] = state
        self.save_state(state)

        logger.info(f"Created workflow state for {company} - {role}")
        return state

    def update_state(self,
                    job_id: str,
                    status: Optional[WorkflowStatus] = None,
                    **kwargs) -> WorkflowState:
        """Update a workflow state.

        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Other fields to update

        Returns:
            Updated workflow state
        """
        if job_id not in self.active_states:
            # Try to load from disk
            state = self.load_state(job_id)
            if not state:
                raise ValueError(f"No state found for job {job_id}")
            self.active_states[job_id] = state

        state = self.active_states[job_id]

        if status:
            state.status = status
            logger.info(f"Status updated to {status.value} for {state.company}")

        # Update other fields
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

        state.updated_at = datetime.utcnow()
        self.save_state(state)

        return state

    def get_state(self, job_id: str) -> Optional[WorkflowState]:
        """Get a workflow state.

        Args:
            job_id: Job identifier

        Returns:
            Workflow state or None if not found
        """
        if job_id in self.active_states:
            return self.active_states[job_id]

        # Try to load from disk
        return self.load_state(job_id)

    def save_state(self, state: WorkflowState) -> None:
        """Save state to disk.

        Args:
            state: State to save
        """
        state_file = self.state_dir / f"{state.job_id}.json"

        try:
            with open(state_file, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
            logger.debug(f"Saved state for {state.job_id}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_state(self, job_id: str) -> Optional[WorkflowState]:
        """Load state from disk.

        Args:
            job_id: Job identifier

        Returns:
            Workflow state or None if not found
        """
        state_file = self.state_dir / f"{job_id}.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            return WorkflowState.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    def list_states(self,
                   status: Optional[WorkflowStatus] = None,
                   workflow_type: Optional[str] = None,
                   limit: int = 100) -> List[WorkflowState]:
        """List workflow states with optional filters.

        Args:
            status: Filter by status
            workflow_type: Filter by workflow type
            limit: Maximum number of states to return

        Returns:
            List of workflow states
        """
        states = []

        # Load all state files
        for state_file in self.state_dir.glob("*.json"):
            state = self.load_state(state_file.stem)
            if state:
                if status and state.status != status:
                    continue
                if workflow_type and state.workflow_type != workflow_type:
                    continue
                states.append(state)

        # Sort by updated_at descending
        states.sort(key=lambda s: s.updated_at, reverse=True)

        return states[:limit]

    def clear_state(self, job_id: str) -> None:
        """Clear a workflow state.

        Args:
            job_id: Job identifier
        """
        # Remove from memory
        if job_id in self.active_states:
            del self.active_states[job_id]

        # Remove from disk
        state_file = self.state_dir / f"{job_id}.json"
        if state_file.exists():
            state_file.unlink()
            logger.info(f"Cleared state for {job_id}")

    def get_metrics(self, job_id: str) -> Dict[str, Any]:
        """Get metrics for a workflow.

        Args:
            job_id: Job identifier

        Returns:
            Metrics dictionary
        """
        state = self.get_state(job_id)
        if not state:
            return {}

        # Calculate duration
        duration = (state.updated_at - state.created_at).total_seconds()

        metrics = {
            "job_id": job_id,
            "company": state.company,
            "role": state.role,
            "status": state.status.value,
            "duration_seconds": duration,
            "workflow_type": state.workflow_type,
            **state.metrics
        }

        # Add scoring if available
        if state.scoring_result:
            metrics["rubric_score"] = state.scoring_result.get("total_score", 0)
            metrics["score_recommendation"] = state.scoring_result.get("recommendation", "")

        # Add error count
        metrics["error_count"] = len(state.errors)

        return metrics