"""Versioned Export Agent - Saves applications with versioned file naming."""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger
from core import AgentMessage, MessageType

logger = get_logger("versioned_export_agent")


class VersionedExportAgent(BaseAgent):
    """Saves generated applications with versioned file naming."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the versioned export agent.

        Args:
            config: Agent configuration
        """
        super().__init__("versioned_export_agent", config, logger)

        # Set base directory for applications
        self.base_dir = Path(config.get('export_dir', 'data/applications'))
        self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"VersionedExportAgent initialized with base directory: {self.base_dir}")

    async def process(self, data: Any) -> AgentResponse:
        """Process export request with versioning.

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

            # Handle version specification
            version_number = data.get('version', None)  # If specified, use this version
            force_new_version = data.get('force_new_version', False)

            # Clean company and role names for filename
            company = self._sanitize_filename(job_data.get('company', 'Unknown'))
            role = self._sanitize_filename(job_data.get('role', 'PM'))

            # Create folder if it doesn't exist
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            folder_name = f"{timestamp}_{company}_{role}"
            app_dir = self.base_dir / folder_name
            app_dir.mkdir(parents=True, exist_ok=True)

            # Determine version numbers for each document type
            versions = {}

            if version_number:
                # Use specified version for all documents
                versions['resume'] = version_number
                versions['cover_letter'] = version_number
            else:
                # Auto-detect next version numbers
                versions['resume'] = self._get_next_version(app_dir, company, 'PM', 'resume')
                versions['cover_letter'] = self._get_next_version(app_dir, company, 'PM', 'cover_letter')

            # Create file names with new convention: [company]_[position]_[document]-V[#]
            resume_filename = f"{company}_{role}_resume-V{versions['resume']}.md"
            cover_filename = f"{company}_{role}_cover_letter-V{versions['cover_letter']}.md"
            metadata_filename = f"{company}_{role}_metadata-V{max(versions.values())}.json"

            # Save resume
            resume_path = app_dir / resume_filename
            with open(resume_path, 'w') as f:
                f.write(content_result.get('resume', ''))
            logger.info(f"Saved resume to {resume_path}")

            # Save cover letter
            cover_path = app_dir / cover_filename
            with open(cover_path, 'w') as f:
                f.write(content_result.get('cover_letter', ''))
            logger.info(f"Saved cover letter to {cover_path}")

            # Save metadata with version info
            metadata = {
                'job_data': job_data,
                'version_info': {
                    'resume_version': versions['resume'],
                    'cover_letter_version': versions['cover_letter'],
                    'generated_at': datetime.now().isoformat(),
                    'folder': folder_name
                },
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
                'export_timestamp': timestamp
            }

            metadata_path = app_dir / metadata_filename
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}")

            # Save job description with version
            jd_filename = f"{company}_{role}_job_description-V{max(versions.values())}.txt"
            if job_data.get('description'):
                jd_path = app_dir / jd_filename
                with open(jd_path, 'w') as f:
                    f.write(job_data['description'])
                logger.info(f"Saved job description to {jd_path}")

            # Create version summary
            version_summary = self._create_version_summary(app_dir, company, role)
            summary_path = app_dir / f"{company}_{role}_version_summary.md"
            with open(summary_path, 'w') as f:
                f.write(version_summary)

            # Build export result
            export_result = {
                'folder': folder_name,
                'versions': versions,
                'files': {
                    'resume': resume_filename,
                    'cover_letter': cover_filename,
                    'metadata': metadata_filename,
                    'job_description': jd_filename,
                    'version_summary': f"{company}_{role}_version_summary.md"
                },
                'paths': {
                    'resume': str(resume_path),
                    'cover_letter': str(cover_path),
                    'metadata': str(metadata_path)
                },
                'status': 'success',
                'message': f'Versioned application saved to {app_dir}'
            }

            logger.info(f"Export complete: {export_result['files']}")

            return AgentResponse(
                success=True,
                result=export_result,
                metrics={
                    'files_created': len(export_result['files']),
                    'versions_created': versions,
                    'folder_size_kb': self._get_folder_size(app_dir)
                }
            )

        except Exception as e:
            logger.error(f"Versioned export failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    def _get_next_version(self, app_dir: Path, company: str, role: str, doc_type: str) -> int:
        """Get the next version number for a document type."""

        # Pattern: [company]_[role]_[doc_type]-V[number].md
        pattern = f"{company}_{role}_{doc_type}-V(\\d+)\\.md"

        versions = []
        if app_dir.exists():
            for file in app_dir.glob(f"{company}_{role}_{doc_type}-V*.md"):
                match = re.search(r'-V(\d+)\.md$', file.name)
                if match:
                    versions.append(int(match.group(1)))

        return max(versions) + 1 if versions else 1

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')

        # Replace spaces and special chars with underscores
        name = re.sub(r'[^\w\-_]', '_', name)

        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)

        # Remove leading/trailing underscores
        name = name.strip('_')

        # Limit length
        return name[:30]

    def _create_version_summary(self, app_dir: Path, company: str, role: str) -> str:
        """Create a summary of all versions for this application."""

        summary = f"""# Version Summary: {company} {role}

## Document Versions

### Resume Versions
"""

        # Find all resume versions
        resume_files = sorted(app_dir.glob(f"{company}_{role}_resume-V*.md"),
                             key=lambda x: int(re.search(r'-V(\d+)\.md$', x.name).group(1)))

        for resume_file in resume_files:
            match = re.search(r'-V(\d+)\.md$', resume_file.name)
            if match:
                version = match.group(1)
                modified_time = datetime.fromtimestamp(resume_file.stat().st_mtime)
                summary += f"- V{version}: {resume_file.name} (Modified: {modified_time.strftime('%Y-%m-%d %H:%M')})\n"

        summary += "\n### Cover Letter Versions\n"

        # Find all cover letter versions
        cover_files = sorted(app_dir.glob(f"{company}_{role}_cover_letter-V*.md"),
                           key=lambda x: int(re.search(r'-V(\d+)\.md$', x.name).group(1)))

        for cover_file in cover_files:
            match = re.search(r'-V(\d+)\.md$', cover_file.name)
            if match:
                version = match.group(1)
                modified_time = datetime.fromtimestamp(cover_file.stat().st_mtime)
                summary += f"- V{version}: {cover_file.name} (Modified: {modified_time.strftime('%Y-%m-%d %H:%M')})\n"

        # Get latest version numbers
        latest_resume_version = max([int(re.search(r'-V(\d+)\.md$', f.name).group(1)) for f in resume_files]) if resume_files else 1
        latest_cover_version = max([int(re.search(r'-V(\d+)\.md$', f.name).group(1)) for f in cover_files]) if cover_files else 1

        summary += f"""
## Latest Versions
- **Resume**: V{latest_resume_version}
- **Cover Letter**: V{latest_cover_version}

## File Naming Convention
- Format: `[company]_[position]_[document]-V[#].md`
- Examples:
  - `{company}_{role}_resume-V1.md`
  - `{company}_{role}_cover_letter-V1.md`
  - `{company}_{role}_metadata-V1.json`

## Version Control Notes
- New versions created when significant edits are made
- Each document type has independent versioning
- Metadata file uses the highest version number from documents
"""

        return summary

    def _get_folder_size(self, folder: Path) -> float:
        """Get total size of folder in KB."""
        total_size = 0
        for file in folder.glob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return round(total_size / 1024, 2)

    async def save_improved_version(self,
                                  app_dir: Path,
                                  company: str,
                                  role: str,
                                  improved_content: Dict[str, str],
                                  improvement_notes: str = "") -> Dict[str, Any]:
        """Save an improved version of documents.

        Args:
            app_dir: Application directory
            company: Company name
            role: Role name
            improved_content: Dict with 'resume' and/or 'cover_letter' keys
            improvement_notes: Notes about what was improved

        Returns:
            Result with new version info
        """

        versions_created = {}
        files_created = []

        # Save improved resume if provided
        if 'resume' in improved_content:
            next_version = self._get_next_version(app_dir, company, role, 'resume')
            resume_filename = f"{company}_{role}_resume-V{next_version}.md"
            resume_path = app_dir / resume_filename

            with open(resume_path, 'w') as f:
                f.write(improved_content['resume'])

            versions_created['resume'] = next_version
            files_created.append(resume_filename)
            logger.info(f"Saved improved resume V{next_version}: {resume_path}")

        # Save improved cover letter if provided
        if 'cover_letter' in improved_content:
            next_version = self._get_next_version(app_dir, company, role, 'cover_letter')
            cover_filename = f"{company}_{role}_cover_letter-V{next_version}.md"
            cover_path = app_dir / cover_filename

            with open(cover_path, 'w') as f:
                f.write(improved_content['cover_letter'])

            versions_created['cover_letter'] = next_version
            files_created.append(cover_filename)
            logger.info(f"Saved improved cover letter V{next_version}: {cover_path}")

        # Save improvement notes
        if improvement_notes:
            notes_filename = f"{company}_{role}_improvements-V{max(versions_created.values())}.md"
            notes_path = app_dir / notes_filename

            with open(notes_path, 'w') as f:
                f.write(f"# Improvements Made - Version {max(versions_created.values())}\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"## Changes Made\n{improvement_notes}\n\n")
                f.write(f"## Files Updated\n")
                for doc_type, version in versions_created.items():
                    f.write(f"- {doc_type}: V{version}\n")

            files_created.append(notes_filename)

        # Update version summary
        version_summary = self._create_version_summary(app_dir, company, role)
        summary_path = app_dir / f"{company}_{role}_version_summary.md"
        with open(summary_path, 'w') as f:
            f.write(version_summary)

        return {
            'versions_created': versions_created,
            'files_created': files_created,
            'improvement_notes_saved': bool(improvement_notes)
        }