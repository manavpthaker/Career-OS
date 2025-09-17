"""Workflow execution engine with DAG support."""

import asyncio
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from pathlib import Path
import yaml

from utils import get_logger
from .message_bus import MessageBus, AgentMessage, MessageType
from .state_manager import StateManager, WorkflowState, WorkflowStatus

logger = get_logger("workflow_engine")


@dataclass
class WorkflowStep:
    """A step in the workflow."""
    name: str
    agent: str
    depends_on: List[str] = None
    parallel: bool = False
    timeout: float = 60.0
    retry_count: int = 1

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    name: str
    description: str
    steps: List[WorkflowStep]
    emphasis: str  # management, impact, execution
    positioning_angle: str
    voice_blend: Dict[str, int]


class WorkflowEngine:
    """Executes workflows with dependency management."""

    def __init__(self,
                 message_bus: MessageBus,
                 state_manager: StateManager,
                 config_dir: str = "config/workflows"):
        """Initialize the workflow engine.

        Args:
            message_bus: Message bus for agent communication
            state_manager: State manager for persistence
            config_dir: Directory containing workflow configurations
        """
        self.message_bus = message_bus
        self.state_manager = state_manager
        self.config_dir = Path(config_dir)
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.agents: Dict[str, Any] = {}

        # Load workflow configurations
        self._load_workflows()

    def _load_workflows(self) -> None:
        """Load workflow configurations from YAML files."""
        if not self.config_dir.exists():
            logger.warning(f"Workflow config directory not found: {self.config_dir}")
            return

        for config_file in self.config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)

                # Parse workflow config
                steps = [WorkflowStep(**step) for step in data.get('steps', [])]

                workflow = WorkflowConfig(
                    name=data['name'],
                    description=data.get('description', ''),
                    steps=steps,
                    emphasis=data.get('emphasis', 'balanced'),
                    positioning_angle=data.get('positioning_angle', 'general'),
                    voice_blend=data.get('voice_blend', {
                        'gawdat': 50,
                        'mulaney': 30,
                        'maher': 20
                    })
                )

                self.workflows[config_file.stem] = workflow
                logger.info(f"Loaded workflow: {workflow.name}")

            except Exception as e:
                logger.error(f"Failed to load workflow {config_file}: {e}")

    def register_agent(self, name: str, agent: Any) -> None:
        """Register an agent with the engine.

        Args:
            name: Agent name
            agent: Agent instance
        """
        self.agents[name] = agent
        self.message_bus.register_agent(name, agent)
        logger.info(f"Registered agent: {name}")

    async def execute_workflow(self,
                              workflow_type: str,
                              job_data: Dict[str, Any]) -> WorkflowState:
        """Execute a workflow for a job.

        Args:
            workflow_type: Type of workflow to execute
            job_data: Job information

        Returns:
            Final workflow state
        """
        if workflow_type not in self.workflows:
            # Use default workflow
            workflow_type = self._select_default_workflow(job_data)

        workflow = self.workflows[workflow_type]
        logger.info(f"Executing workflow: {workflow.name}")

        # Create workflow state
        state = self.state_manager.create_state(
            job_id=job_data.get('job_id', 'unknown'),
            job_url=job_data.get('url', ''),
            company=job_data.get('company', ''),
            role=job_data.get('role', ''),
            workflow_type=workflow_type
        )

        # Track completed steps
        completed_steps: Set[str] = set()
        step_results: Dict[str, Any] = {}

        try:
            # Execute workflow steps
            for step in workflow.steps:
                # Check dependencies
                if not all(dep in completed_steps for dep in step.depends_on):
                    logger.warning(f"Dependencies not met for {step.name}")
                    continue

                # Update status based on step
                status = self._get_status_for_step(step.name)
                self.state_manager.update_state(state.job_id, status=status)

                # Execute step
                logger.info(f"Executing step: {step.name}")
                result = await self._execute_step(
                    step=step,
                    workflow=workflow,
                    state=state,
                    job_data=job_data,
                    step_results=step_results
                )

                # Store result
                step_results[step.name] = result
                completed_steps.add(step.name)

                # Update state with result
                self._update_state_with_result(state, step.name, result)

            # Mark as complete
            self.state_manager.update_state(
                state.job_id,
                status=WorkflowStatus.COMPLETE
            )

            logger.info(f"Workflow completed for {state.company}")
            return state

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self.state_manager.update_state(
                state.job_id,
                status=WorkflowStatus.FAILED,
                errors=state.errors + [str(e)]
            )
            raise

    async def _execute_step(self,
                           step: WorkflowStep,
                           workflow: WorkflowConfig,
                           state: WorkflowState,
                           job_data: Dict[str, Any],
                           step_results: Dict[str, Any]) -> Any:
        """Execute a single workflow step.

        Args:
            step: Step to execute
            workflow: Workflow configuration
            state: Current workflow state
            job_data: Job information
            step_results: Results from previous steps

        Returns:
            Step execution result
        """
        agent = self.agents.get(step.agent)
        if not agent:
            raise ValueError(f"Agent not found: {step.agent}")

        # Prepare input for agent
        agent_input = self._prepare_agent_input(
            step=step,
            workflow=workflow,
            state=state,
            job_data=job_data,
            step_results=step_results
        )

        # Execute with retry
        for attempt in range(step.retry_count):
            try:
                # Create message for agent
                message = AgentMessage(
                    sender="workflow_engine",
                    recipient=step.agent,
                    message_type=self._get_message_type_for_step(step.name),
                    data=agent_input,
                    correlation_id=state.job_id
                )

                # Send message and wait for response
                await self.message_bus.send(message)

                # Wait for agent response
                response = await self.message_bus.wait_for_message(
                    recipient="workflow_engine",
                    correlation_id=state.job_id,
                    timeout=step.timeout
                )

                if response and response.data.get('success'):
                    return response.data.get('result')

                if attempt < step.retry_count - 1:
                    logger.warning(f"Step {step.name} failed, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Step {step.name} execution error: {e}")
                if attempt < step.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise RuntimeError(f"Step {step.name} failed after {step.retry_count} attempts")

    def _prepare_agent_input(self,
                            step: WorkflowStep,
                            workflow: WorkflowConfig,
                            state: WorkflowState,
                            job_data: Dict[str, Any],
                            step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input for an agent based on step and workflow.

        Args:
            step: Current step
            workflow: Workflow configuration
            state: Workflow state
            job_data: Job information
            step_results: Previous step results

        Returns:
            Input dictionary for the agent
        """
        # Base input
        agent_input = {
            'job_data': job_data,
            'workflow_config': {
                'emphasis': workflow.emphasis,
                'positioning_angle': workflow.positioning_angle,
                'voice_blend': workflow.voice_blend
            }
        }

        # Add relevant previous results based on step
        if step.name == 'scoring':
            agent_input['research_data'] = step_results.get('research')

        elif step.name == 'positioning':
            agent_input['research_data'] = step_results.get('research')
            agent_input['scoring_result'] = step_results.get('scoring')

        elif step.name == 'content_generation':
            agent_input['research_data'] = step_results.get('research')
            agent_input['scoring_result'] = step_results.get('scoring')
            agent_input['positioning_strategy'] = step_results.get('positioning')

        elif step.name == 'quality_assurance':
            agent_input['generated_content'] = step_results.get('content_generation')
            agent_input['scoring_result'] = step_results.get('scoring')
            agent_input['positioning_strategy'] = step_results.get('positioning')

        return agent_input

    def _get_status_for_step(self, step_name: str) -> WorkflowStatus:
        """Get workflow status for a step name."""
        status_map = {
            'research': WorkflowStatus.RESEARCHING,
            'scoring': WorkflowStatus.SCORING,
            'positioning': WorkflowStatus.POSITIONING,
            'content_generation': WorkflowStatus.GENERATING,
            'quality_assurance': WorkflowStatus.REVIEWING
        }
        return status_map.get(step_name, WorkflowStatus.INITIATED)

    def _get_message_type_for_step(self, step_name: str) -> MessageType:
        """Get message type for a step name."""
        type_map = {
            'research': MessageType.COMPANY_INTEL,
            'scoring': MessageType.SCORING_RESULT,
            'positioning': MessageType.POSITIONING_STRATEGY,
            'content_generation': MessageType.CONTENT_REQUEST,
            'quality_assurance': MessageType.QA_REQUEST
        }
        return type_map.get(step_name, MessageType.STATUS)

    def _update_state_with_result(self,
                                 state: WorkflowState,
                                 step_name: str,
                                 result: Any) -> None:
        """Update workflow state with step result."""
        if step_name == 'research':
            self.state_manager.update_state(
                state.job_id,
                research_data=result
            )
        elif step_name == 'scoring':
            self.state_manager.update_state(
                state.job_id,
                scoring_result=result
            )
        elif step_name == 'positioning':
            self.state_manager.update_state(
                state.job_id,
                positioning_strategy=result
            )
        elif step_name == 'content_generation':
            self.state_manager.update_state(
                state.job_id,
                generated_content=result
            )
        elif step_name == 'quality_assurance':
            self.state_manager.update_state(
                state.job_id,
                qa_result=result
            )

    def _select_default_workflow(self, job_data: Dict[str, Any]) -> str:
        """Select default workflow based on job data."""
        role = job_data.get('role', '').lower()

        if 'director' in role or 'vp' in role or 'head' in role:
            return 'director_level'
        elif 'principal' in role or 'staff' in role:
            return 'principal_level'
        else:
            return 'senior_level'