#!/usr/bin/env python3
"""Test full pipeline with export."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_full_pipeline():
    """Test complete pipeline from job to export."""

    orchestrator = JobSearchOrchestrator()

    # Sample job description for a senior product role
    job_description = """
    Senior Product Manager - AI Products
    
    We're looking for an experienced Product Manager to lead our AI initiatives.
    
    Requirements:
    • 7+ years of product management experience
    • Experience building AI/ML products
    • Track record of preventing churn and improving efficiency
    • Strong data analysis skills
    • Experience with B2B SaaS products
    • Leadership experience with cross-functional teams
    
    What you'll do:
    • Define and execute AI product strategy
    • Work with engineering to ship ML features
    • Analyze user data to identify opportunities
    • Lead cross-functional teams
    • Drive revenue growth and retention
    
    Nice to have:
    • Experience with marketplace or e-commerce platforms
    • Startup experience
    • Experience raising funding
    """

    print("\n" + "="*60)
    print("🚀 FULL PIPELINE TEST WITH EXPORT")
    print("="*60)

    # Test job data
    job_data = {
        'job_id': 'test-pipeline-001',
        'url': 'https://example.com/senior-pm-ai',
        'company': 'TechCorp AI',
        'role': 'Senior Product Manager - AI Products',
        'description': job_description
    }

    # Step 1: Score the job
    print("\n📊 Step 1: Scoring Job...")
    scoring_result = await orchestrator.workflow_engine.agents['scoring_agent'].process({
        'job_data': job_data
    })
    
    if scoring_result.success:
        score = scoring_result.result.get('total_score', 0)
        print(f"✅ Score: {score}/100")
        print(f"📋 Recommendation: {scoring_result.result.get('recommendation')}")
    else:
        print(f"❌ Scoring failed: {scoring_result.errors}")
        return

    # Step 2: Get positioning strategy
    print("\n🎯 Step 2: Determining Positioning Strategy...")
    positioning_result = await orchestrator.workflow_engine.agents['positioning_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result
    })
    
    if positioning_result.success:
        strategy = positioning_result.result.get('strategy_name')
        print(f"✅ Strategy: {strategy}")
        print(f"📢 Hook: {positioning_result.result.get('hook')[:80]}...")
    else:
        print(f"❌ Positioning failed: {positioning_result.errors}")
        return

    # Step 3: Generate content
    print("\n📝 Step 3: Generating Application Content...")
    content_result = await orchestrator.workflow_engine.agents['content_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result,
        'positioning_strategy': positioning_result.result
    })
    
    if content_result.success:
        print(f"✅ Content generated successfully")
        print(f"📊 Voice blend: {content_result.result.get('voice_blend')}")
        print(f"📄 Resume: {content_result.metrics.get('resume_words')} words")
        print(f"💌 Cover letter: {content_result.metrics.get('cover_letter_words')} words")
    else:
        print(f"❌ Content generation failed: {content_result.errors}")
        return

    # Step 4: Export to local filesystem
    print("\n💾 Step 4: Exporting Application...")
    export_result = await orchestrator.workflow_engine.agents['export_agent'].process({
        'job_data': job_data,
        'content_result': content_result.result,
        'scoring_result': scoring_result.result,
        'positioning_strategy': positioning_result.result
    })
    
    if export_result.success:
        print(f"✅ Application exported successfully!")
        print(f"📁 Folder: {export_result.result.get('folder')}")
        print(f"📍 Location: {export_result.result.get('message')}")
        print("\n📂 Files created:")
        for file_type, path in export_result.result.get('paths', {}).items():
            print(f"  • {file_type}: {Path(path).name}")
    else:
        print(f"❌ Export failed: {export_result.errors}")
        return

    # Display sample content
    print("\n" + "="*60)
    print("📄 RESUME PREVIEW")
    print("="*60)
    resume_preview = content_result.result.get('resume', '')[:600]
    print(resume_preview + "...\n")

    print("="*60)
    print("💌 COVER LETTER PREVIEW")
    print("="*60)
    cover_preview = content_result.result.get('cover_letter', '')[:600]
    print(cover_preview + "...\n")

    print("="*60)
    print("✨ PIPELINE COMPLETE!")
    print("="*60)
    print(f"\n📁 Full application saved to: data/applications/{export_result.result.get('folder')}")
    print("\n📋 Summary:")
    print(f"  • Company: {job_data['company']}")
    print(f"  • Role: {job_data['role']}")
    print(f"  • Score: {score}/100")
    print(f"  • Strategy: {strategy}")
    print(f"  • Files: {len(export_result.result.get('paths', {}))}")


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())