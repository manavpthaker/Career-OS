#!/usr/bin/env python3
"""
Career-OS Setup for Claude Code Users
Interactive setup that builds your professional narrative and validates configuration.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Interactive Career-OS setup."""
    print("🚀 Career-OS Setup")
    print("=" * 50)
    print("Building your professional narrative for job search automation.\n")

    # Check prerequisites
    check_prerequisites()

    # Create user data directory
    setup_directories()

    # Interactive narrative building
    narrative = build_narrative_interactive()

    # Save narrative
    save_narrative(narrative)

    # Test with sample job
    test_setup()

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python claude-code/apply_to_job.py --url [job-url]")
    print("2. Or use prompts directly: copy prompts/01_analyze_job.md to Claude/ChatGPT")
    print("3. Review examples/ directory for samples")

def check_prerequisites():
    """Check if basic requirements are met."""
    print("🔍 Checking prerequisites...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)

    # Check if we're in the right directory
    if not Path("prompts").exists():
        print("❌ Please run from career-os root directory")
        sys.exit(1)

    print("✅ Prerequisites met")

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")

    directories = [
        "user_data",
        "user_data/narratives",
        "user_data/applications",
        "user_data/job_analyses"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Directories created")

def build_narrative_interactive():
    """Interactive narrative building."""
    print("\n📝 Building your professional narrative...")
    print("This creates the foundation for all job applications.\n")

    # Load template
    with open("templates/narrative_template.json") as f:
        template = json.load(f)

    narrative = {}

    # Personal info
    print("📋 Personal Information")
    narrative["personal_info"] = {
        "name": input("Full name: "),
        "email": input("Email: "),
        "phone": input("Phone (optional): ") or None,
        "location": input("Location (City, State): "),
        "linkedin": input("LinkedIn (just username): "),
        "github": input("GitHub (optional): ") or None,
        "portfolio": input("Portfolio URL (optional): ") or None
    }

    # Professional identity
    print("\n🎯 Professional Identity")
    print("This is how you'll be positioned across all applications.")
    narrative["professional_identity"] = {
        "positioning_statement": input("Professional identity (2-3 sentences): "),
        "years_experience": input("Years of experience: ") + "+ years",
        "domain_expertise": input("Domain expertise (e.g., 'B2B SaaS, marketplace platforms'): "),
        "level": input("Current/target level (e.g., 'Senior PM', 'Principal PM'): ")
    }

    # Current position
    print("\n💼 Current/Recent Position")
    narrative["current_position"] = {
        "title": input("Job title: "),
        "company": input("Company: "),
        "company_context": input("Company context (stage, industry, size): "),
        "start_date": input("Start date: "),
        "end_date": input("End date (or 'Present'): "),
        "location": input("Location (Remote/City): ")
    }

    # Key achievements
    print("\n🏆 Key Achievements")
    print("Enter 3-5 major achievements with specific metrics.")
    narrative["key_achievements"] = []

    for i in range(5):
        print(f"\nAchievement {i+1} (press Enter to skip):")
        metric = input(f"  Metric (e.g., '$2.3M revenue impact'): ")
        if not metric:
            break
        context = input(f"  Context (brief explanation): ")
        timeframe = input(f"  When (e.g., '2023', 'Q2 2024'): ")

        narrative["key_achievements"].append({
            "metric": metric,
            "context": context,
            "timeframe": timeframe
        })

    # Technical skills
    print("\n💻 Technical Skills")
    narrative["technical_skills"] = {
        "product_tools": input("Product tools (comma-separated): ").split(", "),
        "technical_skills": input("Technical skills (comma-separated): ").split(", "),
        "ai_ml_experience": input("AI/ML experience (comma-separated): ").split(", "),
        "platforms": input("Platforms/frameworks (comma-separated): ").split(", ")
    }

    # Target roles
    print("\n🎯 Target Roles")
    target_roles = []
    for i in range(3):
        role = input(f"Target role {i+1} (press Enter to finish): ")
        if not role:
            break
        target_roles.append(role)
    narrative["target_roles"] = target_roles

    # Value proposition
    print("\n💡 Value Proposition")
    narrative["value_proposition"] = {
        "unique_combination": input("What makes your background unique: "),
        "problem_solver_type": input("What problems you excel at solving: "),
        "ideal_company_stage": input("Ideal company stage/type: ")
    }

    # Add metadata
    narrative["notes"] = {
        "created_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "verification_status": "User-provided, needs verification",
        "setup_version": "1.0"
    }

    return narrative

def save_narrative(narrative):
    """Save the narrative to user data."""
    print("\n💾 Saving narrative...")

    # Save main narrative
    narrative_path = Path("user_data/narratives/main_narrative.json")
    with open(narrative_path, "w") as f:
        json.dump(narrative, f, indent=2)

    print(f"✅ Narrative saved to {narrative_path}")

def test_setup():
    """Test the setup with a sample job."""
    print("\n🧪 Testing setup...")

    # Check if sample job exists
    sample_job_path = Path("examples/sample_job_analysis/sample_job.md")
    if sample_job_path.exists():
        print("✅ Sample job found for testing")
        print(f"📄 You can test with: {sample_job_path}")
    else:
        print("⚠️  No sample job found - you'll need a real job posting to test")

    # Validate narrative
    narrative_path = Path("user_data/narratives/main_narrative.json")
    if narrative_path.exists():
        with open(narrative_path) as f:
            narrative = json.load(f)

        # Basic validation
        required_fields = ["personal_info", "professional_identity", "key_achievements"]
        missing_fields = [field for field in required_fields if field not in narrative]

        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
        else:
            print("✅ Narrative validation passed")

def get_ai_assistance_prompt():
    """Generate prompt for AI assistance with narrative building."""
    return """
I need help building my professional narrative for job applications. Here's my background:

[PASTE YOUR RESUME OR LINKEDIN PROFILE HERE]

Please help me create:

1. **Professional Identity**: 2-3 sentence positioning statement
2. **Key Achievements**: 5-7 major wins with specific metrics
3. **Value Proposition**: What makes me unique
4. **Technical Skills**: Organized by category
5. **Target Positioning**: How to frame for [TARGET ROLE TYPE]

Format as JSON compatible with career-os narrative structure.
Be specific with metrics and avoid generic corporate language.
"""

if __name__ == "__main__":
    main()