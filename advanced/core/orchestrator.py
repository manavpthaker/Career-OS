"""Main orchestrator for the job search automation system."""

import asyncio
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import uuid
import yaml

from utils import get_logger, log_kv
from core.message_bus import MessageBus
from core.state_manager import StateManager, WorkflowStatus
from core.workflow_engine import WorkflowEngine

# Import agents
from agents.research_agent import ResearchAgent
from agents.scoring_agent import ScoringAgent
from agents.positioning_agent import PositioningAgent
from agents.content_agent import ContentAgent
from agents.export_agent import ExportAgent

logger = get_logger("orchestrator")


class JobSearchOrchestrator:
    """Main orchestrator for job search automation."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the orchestrator.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)

        # Initialize core components
        self.message_bus = MessageBus()
        self.state_manager = StateManager(self.config.get('state_dir', 'data/state'))
        self.workflow_engine = WorkflowEngine(
            self.message_bus,
            self.state_manager,
            self.config.get('workflow_dir', 'config/workflows')
        )

        # Initialize agents
        self._initialize_agents()

        logger.info("Orchestrator initialized successfully")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")

        # Default configuration
        return {
            'agents': {
                'research': {'cache_ttl_hours': 24, 'enable_web_search': True},
                'scoring': {'confidence_threshold': 0.7},
                'positioning': {'narrative_paths': ['knowledge/narrative']},
                'content': {'template_dir': 'templates'},
                'qa': {'strict_mode': True},
                'export': {'drive_enabled': False}
            },
            'workflow': {
                'default_type': 'auto',
                'timeout': 300,
                'max_parallel': 3
            },
            'output': {
                'applications_dir': 'data/applications',
                'logs_dir': 'logs'
            }
        }

    def _initialize_agents(self) -> None:
        """Initialize all agents and register with workflow engine."""
        agent_configs = self.config.get('agents', {})

        # Initialize Research Agent
        research_agent = ResearchAgent(agent_configs.get('research', {}))
        self.workflow_engine.register_agent('research_agent', research_agent)
        self.message_bus.register_agent('research_agent', research_agent)

        # Initialize Scoring Agent
        scoring_agent = ScoringAgent(agent_configs.get('scoring', {}))
        self.workflow_engine.register_agent('scoring_agent', scoring_agent)
        self.message_bus.register_agent('scoring_agent', scoring_agent)

        # Initialize Positioning Agent
        positioning_agent = PositioningAgent(agent_configs.get('positioning', {}))
        self.workflow_engine.register_agent('positioning_agent', positioning_agent)
        self.message_bus.register_agent('positioning_agent', positioning_agent)

        # Initialize Content Agent
        content_agent = ContentAgent(agent_configs.get('content', {}))
        self.workflow_engine.register_agent('content_agent', content_agent)
        self.message_bus.register_agent('content_agent', content_agent)

        # Initialize Export Agent
        export_agent = ExportAgent(agent_configs.get('export', {}))
        self.workflow_engine.register_agent('export_agent', export_agent)
        self.message_bus.register_agent('export_agent', export_agent)

        # Placeholder for other agents (to be implemented)
        # QAAgent still to come

        logger.info(f"Initialized {len(self.workflow_engine.agents)} agents")

    async def process_job(self,
                         job_url: str,
                         company: Optional[str] = None,
                         role: Optional[str] = None,
                         workflow_type: str = 'auto') -> Dict[str, Any]:
        """Process a job application.

        Args:
            job_url: URL of the job posting
            company: Company name (optional, will extract if not provided)
            role: Role title (optional, will extract if not provided)
            workflow_type: Type of workflow to use ('auto', 'director_level', 'principal_level', 'senior_level')

        Returns:
            Application results
        """
        start_time = datetime.utcnow()
        job_id = str(uuid.uuid4())[:8]

        logger.info(f"Processing job: {company or 'Unknown'} - {role or 'Unknown'}")
        log_kv(logger, "job_processing_started",
            job_id=job_id,
            url=job_url,
            company=company,
            role=role,
            workflow_type=workflow_type)

        try:
            # Prepare job data
            job_data = {
                'job_id': job_id,
                'url': job_url,
                'company': company or self._extract_company_from_url(job_url),
                'role': role or 'Product Manager',
                'description': ''  # Would be fetched from URL in production
            }

            # Start message bus
            await self.message_bus.start()

            # Execute workflow
            state = await self.workflow_engine.execute_workflow(
                workflow_type=workflow_type,
                job_data=job_data
            )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Prepare results
            results = {
                'job_id': job_id,
                'status': 'success' if state.status == WorkflowStatus.COMPLETE else 'failed',
                'processing_time': processing_time,
                'scoring': state.scoring_result,
                'positioning': state.positioning_strategy,
                'content': state.generated_content,
                'qa': state.qa_result,
                'workflow_type': workflow_type,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Save results
            self._save_results(results, job_data)

            # Log completion
            log_kv(logger, "job_processing_complete",
                job_id=job_id,
                status=results['status'],
                processing_time=processing_time,
                score=state.scoring_result.get('total_score') if state.scoring_result else None)

            return results

        except Exception as e:
            logger.error(f"Job processing failed: {e}")
            return {
                'job_id': job_id,
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.utcnow() - start_time).total_seconds()
            }

        finally:
            # Stop message bus
            await self.message_bus.stop()

    async def score_job(self, job_url: str, job_description: str = None) -> Dict[str, Any]:
        """Score a job without generating full application.

        Args:
            job_url: URL of the job posting
            job_description: Optional job description text

        Returns:
            Scoring results
        """
        logger.info(f"Scoring job: {job_url}")

        try:
            # Initialize minimal agents for scoring
            await self.message_bus.start()

            # Create job data
            job_data = {
                'job_id': str(uuid.uuid4())[:8],
                'url': job_url,
                'description': job_description or '',
                'company': self._extract_company_from_url(job_url)
            }

            # Run research and scoring in parallel
            research_task = self.workflow_engine.agents['research_agent'].process({
                'job_data': job_data
            })
            scoring_task = self.workflow_engine.agents['scoring_agent'].process({
                'job_data': job_data
            })

            research_result, scoring_result = await asyncio.gather(
                research_task, scoring_task
            )

            # Return combined results
            return {
                'url': job_url,
                'company': job_data['company'],
                'score': scoring_result.result.get('total_score') if scoring_result.success else 0,
                'breakdown': scoring_result.result.get('category_breakdown') if scoring_result.success else {},
                'recommendation': scoring_result.result.get('recommendation') if scoring_result.success else 'Unable to score',
                'research_quality': research_result.result.get('research_quality') if research_result.success else 'low'
            }

        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return {
                'url': job_url,
                'error': str(e)
            }

        finally:
            await self.message_bus.stop()

    async def batch_process(self,
                           job_urls: List[str],
                           workflow_type: str = 'auto',
                           parallel: int = 1) -> List[Dict[str, Any]]:
        """Process multiple jobs.

        Args:
            job_urls: List of job URLs
            workflow_type: Workflow type to use
            parallel: Number of parallel jobs to process

        Returns:
            List of results
        """
        logger.info(f"Batch processing {len(job_urls)} jobs")

        results = []

        # Process in batches
        for i in range(0, len(job_urls), parallel):
            batch = job_urls[i:i + parallel]

            # Process batch in parallel
            tasks = [
                self.process_job(url, workflow_type=workflow_type)
                for url in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    results.append({
                        'status': 'error',
                        'error': str(result)
                    })
                else:
                    results.append(result)

        return results

    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL.

        Args:
            url: Job URL

        Returns:
            Company name or 'Unknown'
        """
        # Simple extraction based on common patterns
        url_lower = url.lower()

        # Known patterns
        if 'greenhouse.io' in url_lower:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if 'greenhouse.io' in part and i > 0:
                    return parts[i-1].replace('-', ' ').title()

        elif 'lever.co' in url_lower:
            parts = url.split('/')
            for part in parts:
                if part and '.' not in part and len(part) > 2:
                    return part.replace('-', ' ').title()

        elif 'workday' in url_lower:
            # Workday URLs often have company name in subdomain
            if 'wd1.myworkdayjobs.com' in url_lower or 'wd5.myworkdayjobs.com' in url_lower:
                parts = url.split('/')
                for part in parts:
                    if part and not part.startswith('http') and '.' not in part:
                        return part.replace('_', ' ').replace('-', ' ').title()

        return 'Unknown'

    def _save_results(self, results: Dict[str, Any], job_data: Dict[str, Any]) -> None:
        """Save application results to disk.

        Args:
            results: Application results
            job_data: Job information
        """
        try:
            # Create output directory
            output_dir = Path(self.config['output']['applications_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create job-specific directory
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            company_name = job_data['company'].replace(' ', '_').replace('/', '_')
            role_name = job_data.get('role', 'Unknown').replace(' ', '_').replace('/', '_')
            job_dir = output_dir / f"{timestamp}_{company_name}_{role_name}"
            job_dir.mkdir(exist_ok=True)

            # Save metadata
            import json
            metadata_file = job_dir / 'metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump({
                    'job_data': job_data,
                    'results': results
                }, f, indent=2)

            # Save generated content if available
            if results.get('content'):
                content = results['content']

                if 'resume' in content:
                    resume_file = job_dir / 'resume.md'
                    with open(resume_file, 'w') as f:
                        f.write(content['resume'])

                if 'cover_letter' in content:
                    cover_file = job_dir / 'cover_letter.md'
                    with open(cover_file, 'w') as f:
                        f.write(content['cover_letter'])

            logger.info(f"Results saved to {job_dir}")

        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a job application.

        Args:
            job_id: Job ID

        Returns:
            Status information
        """
        state = self.state_manager.get_state(job_id)

        if not state:
            return {'status': 'not_found'}

        return {
            'job_id': job_id,
            'status': state.status.value,
            'company': state.company,
            'role': state.role,
            'created_at': state.created_at.isoformat(),
            'updated_at': state.updated_at.isoformat(),
            'score': state.scoring_result.get('total_score') if state.scoring_result else None,
            'recommendation': state.scoring_result.get('recommendation') if state.scoring_result else None
        }

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.message_bus.stop()
        logger.info("Orchestrator cleanup complete")