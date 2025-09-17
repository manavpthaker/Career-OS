#!/usr/bin/env python3
"""Test versioned export functionality."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.versioned_export_agent import VersionedExportAgent

async def test_versioned_export():
    """Test the versioned export system."""

    # Initialize the versioned export agent
    config = {'export_dir': 'data/applications'}
    export_agent = VersionedExportAgent(config)

    # Sample data for testing
    job_data = {
        'company': 'MagicSchool AI',
        'role': 'Product Manager',
        'description': 'Sample job description for testing versioning...'
    }

    content_result = {
        'resume': """# **[YOUR_NAME]**

[YOUR_CITY, STATE] | [[YOUR_EMAIL]](mailto:[YOUR_EMAIL]) | [YOUR_PHONE]

## EXPERIENCE
### Product Manager | [CURRENT_COMPANY] | [START_DATE] - September 2025
- Sample resume content V1
""",
        'cover_letter': """Dear MagicSchool AI Team,

This is version 1 of the cover letter for testing purposes.

Best regards,
[YOUR_NAME]
""",
        'voice_blend': {'mo_gawdat': 40, 'john_mulaney': 40, 'bill_maher': 20}
    }

    scoring_result = {
        'total_score': 82,
        'recommendation': 'Submit after edits',
        'category_breakdown': {
            'Role Alignment': 15.0,
            'Outcomes & Metrics': 12.0,
            'Product Sense': 8.0
        }
    }

    positioning_strategy = {
        'strategy_name': 'execution_excellence',
        'primary_angle': 'AI automation experience',
        'hook': 'My AI automation experience aligns with MagicSchool mission...'
    }

    print("Testing Versioned Export System")
    print("=" * 50)

    # Test 1: Create initial versions (V1)
    print("\n📝 Test 1: Creating initial versions...")

    export_data = {
        'job_data': job_data,
        'content_result': content_result,
        'scoring_result': scoring_result,
        'positioning_strategy': positioning_strategy
    }

    result1 = await export_agent.process(export_data)

    if result1.success:
        print(f"✅ Initial export successful!")
        print(f"   Folder: {result1.result['folder']}")
        print(f"   Files created: {list(result1.result['files'].keys())}")
        print(f"   Versions: {result1.result['versions']}")
    else:
        print(f"❌ Initial export failed: {result1.errors}")
        return

    # Test 2: Create improved versions (V2)
    print("\n📝 Test 2: Creating improved versions...")

    # Modified content for V2
    improved_resume = """# **[YOUR_NAME]**

[YOUR_CITY, STATE] | [[YOUR_EMAIL]](mailto:[YOUR_EMAIL]) | [YOUR_PHONE]

## EXPERIENCE
### Product Manager | [CURRENT_COMPANY] | [START_DATE] - September 2025
- **User-Centered Product Development**: Conducted extensive user research across 1,500+ practitioners to understand workflow challenges, preventing $400K in churn through targeted product improvements and achieving 12% increase in user satisfaction

This is IMPROVED VERSION 2 with better EdTech positioning.
"""

    improved_cover = """Dear MagicSchool AI Team,

At [CURRENT_COMPANY], I prevented $400K in customer churn not through traditional retention tactics, but by deeply understanding how small business practitioners actually work. Through systematic user research with florists, I discovered that product-market fit comes from understanding the daily realities of professional practice - the same insight that drives MagicSchool's success with educators.

This is IMPROVED VERSION 2 with better EdTech angle.

Best regards,
[YOUR_NAME]
"""

    # Update content for V2
    improved_content_result = content_result.copy()
    improved_content_result['resume'] = improved_resume
    improved_content_result['cover_letter'] = improved_cover

    export_data['content_result'] = improved_content_result

    result2 = await export_agent.process(export_data)

    if result2.success:
        print(f"✅ Improved export successful!")
        print(f"   Files created: {list(result2.result['files'].keys())}")
        print(f"   Versions: {result2.result['versions']}")
    else:
        print(f"❌ Improved export failed: {result2.errors}")

    # Test 3: Test manual version improvement
    print("\n📝 Test 3: Testing manual version improvement...")

    app_dir = Path('data/applications') / result1.result['folder']
    company = 'MagicSchool_AI'
    role = 'Product_Manager'

    manual_improvements = {
        'resume': """# **[YOUR_NAME]**

[YOUR_CITY, STATE] | [[YOUR_EMAIL]](mailto:[YOUR_EMAIL]) | [YOUR_PHONE]

## EXPERIENCE
### Product Manager | [CURRENT_COMPANY] | [START_DATE] - September 2025
- **User-Centered Product Development**: Conducted extensive user research across 1,500+ practitioners to understand workflow challenges, preventing $400K in churn through targeted product improvements and achieving 12% increase in user satisfaction

This is MANUALLY IMPROVED VERSION 3 based on rubric feedback.
""",
        'cover_letter': """Dear MagicSchool AI Team,

At [CURRENT_COMPANY], I prevented $400K in customer churn by conducting deep user research with 1,500+ small business practitioners, identifying core workflow pain points and translating insights into product improvements that increased satisfaction 12%.

My initial 90-day plan would focus on: (1) Conducting stakeholder interviews across 5 educator segments to identify highest-impact AI automation opportunities, (2) Establishing baseline metrics for teacher time-savings and satisfaction, and (3) Shipping one quick-win feature to demonstrate immediate value.

This is MANUALLY IMPROVED VERSION with 90-day plan added based on rubric feedback.

Best regards,
[YOUR_NAME]
"""
    }

    improvement_notes = """
## Rubric-Based Improvements for V3

### Changes Made:
1. **Enhanced EdTech Positioning**: Reframed florist research as applicable to educator workflows
2. **Added 90-Day Plan**: Demonstrates strategic thinking (rubric requirement)
3. **Strengthened User Research**: More specific methodology and outcomes
4. **Better Domain Bridge**: Connected practitioner insights to educator needs

### Rubric Score Impact:
- Product Sense & Research: 3 → 4 (added specific research methodology)
- Strategic Thinking: Added 90-day plan paragraph
- Domain Alignment: Better EdTech connection through workflow parallels

### Expected Score Improvement: 82 → 86-88/100
"""

    manual_result = await export_agent.save_improved_version(
        app_dir, company, role, manual_improvements, improvement_notes
    )

    print(f"✅ Manual improvements saved!")
    print(f"   Versions created: {manual_result['versions_created']}")
    print(f"   Files created: {manual_result['files_created']}")
    print(f"   Improvement notes saved: {manual_result['improvement_notes_saved']}")

    # Test 4: Show final file structure
    print("\n📁 Test 4: Final file structure...")

    if app_dir.exists():
        print(f"\nFiles in {app_dir.name}:")
        for file in sorted(app_dir.glob('*')):
            print(f"   📄 {file.name}")

    print("\n🎉 Versioned export system test completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Automatic version detection (V1, V2, V3)")
    print("✅ File naming convention: [company]_[position]_[document]-V[#]")
    print("✅ Version summary generation")
    print("✅ Manual improvement tracking with notes")
    print("✅ Independent versioning per document type")

if __name__ == "__main__":
    asyncio.run(test_versioned_export())