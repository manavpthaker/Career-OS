#!/usr/bin/env python3
"""Main entry point for job search automation v2."""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator
from utils import get_logger

logger = get_logger("main")


@click.group()
@click.option('--config', default='config/config.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Job Search Automation v2 - Enhanced multi-agent system."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.command()
@click.argument('job_url')
@click.option('--company', help='Company name (will extract if not provided)')
@click.option('--role', help='Role title (will extract if not provided)')
@click.option('--workflow', default='auto', help='Workflow type: auto, director_level, principal_level, senior_level')
@click.pass_context
def apply(ctx, job_url, company, role, workflow):
    """Generate a complete job application."""
    click.echo(f"🚀 Processing application for: {job_url}")

    orchestrator = JobSearchOrchestrator(ctx.obj['config'])

    async def run():
        result = await orchestrator.process_job(
            job_url=job_url,
            company=company,
            role=role,
            workflow_type=workflow
        )
        return result

    try:
        result = asyncio.run(run())

        if result['status'] == 'success':
            click.echo(f"✅ Application generated successfully!")

            if result.get('scoring'):
                score = result['scoring'].get('total_score', 0)
                recommendation = result['scoring'].get('recommendation', '')
                click.echo(f"📊 Score: {score}/100")
                click.echo(f"💡 Recommendation: {recommendation}")

            if result.get('positioning'):
                strategy = result['positioning'].get('strategy_name', '')
                click.echo(f"🎯 Positioning: {strategy}")

            click.echo(f"⏱️ Processing time: {result['processing_time']:.2f} seconds")
            click.echo(f"📁 Job ID: {result['job_id']}")

        else:
            click.echo(f"❌ Application failed: {result.get('error', 'Unknown error')}", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('job_url')
@click.option('--description', help='Job description text (optional)')
@click.pass_context
def score(ctx, job_url, description):
    """Score a job posting without generating application."""
    click.echo(f"📊 Scoring job: {job_url}")

    orchestrator = JobSearchOrchestrator(ctx.obj['config'])

    async def run():
        result = await orchestrator.score_job(
            job_url=job_url,
            job_description=description
        )
        return result

    try:
        result = asyncio.run(run())

        if 'error' not in result:
            click.echo(f"\n📋 Company: {result['company']}")
            click.echo(f"🎯 Total Score: {result['score']}/100")
            click.echo(f"💡 Recommendation: {result['recommendation']}")
            click.echo(f"🔍 Research Quality: {result['research_quality']}")

            if result.get('breakdown'):
                click.echo("\n📊 Category Breakdown:")
                for category, score in result['breakdown'].items():
                    click.echo(f"  • {category}: {score:.1f}")

        else:
            click.echo(f"❌ Scoring failed: {result['error']}", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('urls_file')
@click.option('--workflow', default='auto', help='Workflow type')
@click.option('--parallel', default=1, help='Number of parallel jobs')
@click.pass_context
def batch(ctx, urls_file, workflow, parallel):
    """Process multiple job URLs from a file."""
    urls_path = Path(urls_file)

    if not urls_path.exists():
        click.echo(f"❌ File not found: {urls_file}", err=True)
        sys.exit(1)

    # Read URLs from file
    with open(urls_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    click.echo(f"📋 Processing {len(urls)} jobs with {parallel} parallel workers")

    orchestrator = JobSearchOrchestrator(ctx.obj['config'])

    async def run():
        results = await orchestrator.batch_process(
            job_urls=urls,
            workflow_type=workflow,
            parallel=parallel
        )
        return results

    try:
        results = asyncio.run(run())

        # Summary
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = len(results) - successful

        click.echo(f"\n✅ Successful: {successful}")
        click.echo(f"❌ Failed: {failed}")

        # Save batch results
        output_file = Path('batch_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        click.echo(f"📁 Results saved to: {output_file}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('job_id')
@click.pass_context
def status(ctx, job_id):
    """Check status of a job application."""
    orchestrator = JobSearchOrchestrator(ctx.obj['config'])

    async def run():
        result = await orchestrator.get_status(job_id)
        return result

    try:
        result = asyncio.run(run())

        if result['status'] == 'not_found':
            click.echo(f"❌ Job ID not found: {job_id}", err=True)
        else:
            click.echo(f"\n📋 Job ID: {job_id}")
            click.echo(f"🏢 Company: {result['company']}")
            click.echo(f"💼 Role: {result['role']}")
            click.echo(f"📊 Status: {result['status']}")

            if result.get('score') is not None:
                click.echo(f"🎯 Score: {result['score']}/100")
                click.echo(f"💡 Recommendation: {result['recommendation']}")

            click.echo(f"🕒 Created: {result['created_at']}")
            click.echo(f"🕒 Updated: {result['updated_at']}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def health():
    """Check system health and configuration."""
    click.echo("🔍 Checking system health...\n")

    checks = []

    # Check directories
    for dir_path in ['config', 'knowledge', 'agents', 'core', 'utils']:
        path = Path(dir_path)
        exists = path.exists()
        checks.append(('✅' if exists else '❌', f"{dir_path} directory"))

    # Check key files
    for file_path in [
        'knowledge/rubrics/director_rubric.json',
        'knowledge/positioning/strategies.json',
        'knowledge/voice/voice_blend.yaml'
    ]:
        path = Path(file_path)
        exists = path.exists()
        checks.append(('✅' if exists else '❌', f"{file_path}"))

    # Check narrative files
    narrative_path = Path('knowledge/narrative')
    if narrative_path.exists():
        json_files = list(narrative_path.glob('*.json'))
        checks.append(('✅' if json_files else '⚠️', f"Narrative files ({len(json_files)} found)"))

    # Display results
    for status, item in checks:
        click.echo(f"{status} {item}")

    # Check environment variables
    click.echo("\n🔑 Environment Variables:")
    import os
    env_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'TAVILY_API_KEY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            click.echo(f"✅ {var}: {masked}")
        else:
            click.echo(f"⚠️ {var}: Not set")

    # Summary
    all_good = all(status == '✅' for status, _ in checks)
    if all_good:
        click.echo("\n✅ System is healthy and ready!")
    else:
        click.echo("\n⚠️ Some components need attention. Check warnings above.")


if __name__ == '__main__':
    cli()