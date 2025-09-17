"""Export Agent - Saves applications locally as markdown files."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger, log_kv
from core import AgentMessage, MessageType

logger = get_logger("export_agent")


class ExportAgent(BaseAgent):
    """Saves generated applications to local filesystem."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the export agent.

        Args:
            config: Agent configuration
        """
        super().__init__("export_agent", config, logger)

        # Set base directory for applications
        self.base_dir = Path(config.get('export_dir', 'data/applications'))
        self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ExportAgent initialized with base directory: {self.base_dir}")

    async def process(self, data: Any) -> AgentResponse:
        """Process export request.

        Args:
            data: Input containing content, job data, and metadata

        Returns:
            Export response with file paths
        """
        try:
            # Extract inputs
            job_data = data.get('job_data', {})
            content_result = data.get('content_result', {})
            scoring_result = data.get('scoring_result', {})
            positioning_strategy = data.get('positioning_strategy', {})

            # Create folder name
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            company = self._sanitize_filename(job_data.get('company', 'Unknown'))
            role = self._sanitize_filename(job_data.get('role', 'PM'))
            folder_name = f"{timestamp}_{company}_{role}"

            # Create application folder
            app_dir = self.base_dir / folder_name
            app_dir.mkdir(parents=True, exist_ok=True)

            # Log export request
            log_kv(logger, "export_request",
                company=company,
                role=role,
                folder=folder_name,
                score=scoring_result.get('total_score', 0))

            # Save resume
            resume_path = app_dir / "resume.md"
            with open(resume_path, 'w') as f:
                f.write(content_result.get('resume', ''))
            logger.info(f"Saved resume to {resume_path}")

            # Save cover letter
            cover_path = app_dir / "cover_letter.md"
            with open(cover_path, 'w') as f:
                f.write(content_result.get('cover_letter', ''))
            logger.info(f"Saved cover letter to {cover_path}")

            # Save metadata
            metadata = {
                'job_data': job_data,
                'scoring': {
                    'total_score': scoring_result.get('total_score', 0),
                    'recommendation': scoring_result.get('recommendation', ''),
                    'breakdown': scoring_result.get('category_breakdown', {})
                },
                'positioning': {
                    'strategy': positioning_strategy.get('strategy_name', ''),
                    'voice_blend': content_result.get('voice_blend', {}),
                    'hook': positioning_strategy.get('hook', '')
                },
                'generated_at': datetime.now().isoformat(),
                'export_timestamp': timestamp
            }

            metadata_path = app_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}")

            # Save job description if available
            if job_data.get('description'):
                jd_path = app_dir / "job_description.txt"
                with open(jd_path, 'w') as f:
                    f.write(job_data['description'])
                logger.info(f"Saved job description to {jd_path}")

            # Create README with summary
            readme_content = self._create_readme(job_data, scoring_result, positioning_strategy)
            readme_path = app_dir / "README.md"
            with open(readme_path, 'w') as f:
                f.write(readme_content)

            # Build export result
            export_result = {
                'folder': folder_name,
                'paths': {
                    'resume': str(resume_path),
                    'cover_letter': str(cover_path),
                    'metadata': str(metadata_path),
                    'readme': str(readme_path)
                },
                'status': 'success',
                'message': f'Application saved to {app_dir}'
            }

            # Log success
            log_kv(logger, "export_complete",
                folder=folder_name,
                files_created=len(export_result['paths']))

            return AgentResponse(
                success=True,
                result=export_result,
                metrics={
                    'files_created': len(export_result['paths']),
                    'folder_size_kb': self._get_folder_size(app_dir)
                }
            )

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')

        # Replace spaces with underscores
        name = name.replace(' ', '_')

        # Limit length
        return name[:50]

    def _create_readme(self,
                       job_data: Dict[str, Any],
                       scoring_result: Dict[str, Any],
                       positioning_strategy: Dict[str, Any]) -> str:
        """Create README with application summary."""
        readme = f"""# Application Summary

## Job Details
- **Company**: {job_data.get('company', 'Unknown')}
- **Role**: {job_data.get('role', 'Unknown')}
- **URL**: {job_data.get('url', 'N/A')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Scoring Results
- **Total Score**: {scoring_result.get('total_score', 0)}/100
- **Recommendation**: {scoring_result.get('recommendation', 'N/A')}

## Top Scoring Categories
"""
        # Add top categories
        breakdown = scoring_result.get('category_breakdown', {})
        if breakdown:
            sorted_categories = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            for category, score in sorted_categories[:3]:
                readme += f"- {category}: {score:.1f}\n"

        readme += f"""
## Positioning Strategy
- **Strategy**: {positioning_strategy.get('strategy_name', 'N/A')}
- **Primary Angle**: {positioning_strategy.get('primary_angle', 'N/A')}

## Key Metrics Emphasized
"""
        for metric in positioning_strategy.get('key_metrics', [])[:5]:
            readme += f"- {metric}\n"

        readme += """
## Files
- `resume.md` - Tailored resume
- `cover_letter.md` - Personalized cover letter
- `job_description.txt` - Original job posting
- `metadata.json` - Complete application data

## Next Steps
1. Review and finalize the resume and cover letter
2. Submit application through company portal
3. Track application status
"""
        return readme

    def _get_folder_size(self, folder: Path) -> float:
        """Get total size of folder in KB."""
        total_size = 0
        for file in folder.glob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return round(total_size / 1024, 2)

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Incoming message
        """
        if message.message_type == MessageType.EXPORT_REQUEST:
            # Process export request
            result = await self.process(message.data)

            # Send response
            response = AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.EXPORT_COMPLETE,
                data=result.dict(),
                correlation_id=message.correlation_id
            )

            await self.message_bus.send(response)