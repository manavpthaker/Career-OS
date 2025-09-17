#!/usr/bin/env python3
"""
Test script to validate Career-OS setup without interactive input.
"""

import json
from pathlib import Path

def test_basic_structure():
    """Test that basic directory structure is correct."""
    print("🧪 Testing Career-OS Structure")
    print("=" * 40)

    required_dirs = [
        "prompts",
        "claude-code",
        "templates",
        "examples",
        "advanced"
    ]

    required_files = [
        "README.md",
        "QUICKSTART.md",
        "CONTRIBUTING.md",
        "requirements.txt",
        ".gitignore",
        "LICENSE"
    ]

    print("📁 Checking directories...")
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ MISSING")

    print("\n📄 Checking files...")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} MISSING")

def test_prompts():
    """Test that prompt templates exist and are non-empty."""
    print("\n🎯 Testing Prompt Templates")
    print("=" * 40)

    prompts = [
        "prompts/01_analyze_job.md",
        "prompts/02_build_narrative.md",
        "prompts/03_generate_resume.md",
        "prompts/04_write_cover.md",
        "prompts/05_review_quality.md"
    ]

    for prompt in prompts:
        path = Path(prompt)
        if path.exists():
            content = path.read_text()
            if len(content) > 500:  # Reasonable length check
                print(f"  ✅ {prompt} ({len(content)} chars)")
            else:
                print(f"  ⚠️  {prompt} (too short: {len(content)} chars)")
        else:
            print(f"  ❌ {prompt} MISSING")

def test_templates():
    """Test that templates are valid JSON."""
    print("\n📋 Testing Templates")
    print("=" * 40)

    template_path = Path("templates/narrative_template.json")
    if template_path.exists():
        try:
            with open(template_path) as f:
                template = json.load(f)

            required_keys = [
                "personal_info",
                "professional_identity",
                "key_achievements",
                "technical_skills"
            ]

            missing_keys = [key for key in required_keys if key not in template]
            if not missing_keys:
                print(f"  ✅ narrative_template.json (valid JSON with required keys)")
            else:
                print(f"  ⚠️  narrative_template.json (missing keys: {missing_keys})")

        except json.JSONDecodeError as e:
            print(f"  ❌ narrative_template.json (invalid JSON: {e})")
    else:
        print(f"  ❌ narrative_template.json MISSING")

def test_examples():
    """Test that examples exist and are useful."""
    print("\n📚 Testing Examples")
    print("=" * 40)

    examples = [
        "examples/sample_job_analysis/sample_job.md",
        "examples/sample_job_analysis/analysis_output.md",
        "examples/sample_narrative/example_narrative.json"
    ]

    for example in examples:
        path = Path(example)
        if path.exists():
            content = path.read_text()
            if len(content) > 200:
                print(f"  ✅ {example}")
            else:
                print(f"  ⚠️  {example} (content too short)")
        else:
            print(f"  ❌ {example} MISSING")

def test_advanced_system():
    """Test that advanced system was copied correctly."""
    print("\n🔧 Testing Advanced System")
    print("=" * 40)

    key_files = [
        "advanced/README.md",
        "advanced/run.py",
        "advanced/requirements.txt",
        "advanced/agents/",
        "advanced/config/",
        "advanced/knowledge/"
    ]

    for item in key_files:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                files_count = len(list(path.rglob("*")))
                print(f"  ✅ {item} ({files_count} files)")
            else:
                print(f"  ✅ {item}")
        else:
            print(f"  ❌ {item} MISSING")

def test_pii_scrubbing():
    """Test that PII was properly scrubbed."""
    print("\n🧹 Testing PII Scrubbing")
    print("=" * 40)

    # Check a few key files for common PII patterns
    test_files = [
        "advanced/README.md",
        "advanced/config/user_profile.yaml",
        "advanced/knowledge/narrative/verified_facts.json"
    ]

    pii_patterns = [
        "Manav Thaker",
        "manav@mpthaker.xyz",
        "732-995-3007",
        "Rahway, NJ"
    ]

    pii_found = False
    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            for pattern in pii_patterns:
                if pattern in content:
                    print(f"  ⚠️  PII found in {file_path}: {pattern}")
                    pii_found = True

    if not pii_found:
        print("  ✅ No obvious PII patterns found")

def main():
    """Run all tests."""
    test_basic_structure()
    test_prompts()
    test_templates()
    test_examples()
    test_advanced_system()
    test_pii_scrubbing()

    print("\n🎉 Testing Complete!")
    print("\nNext steps:")
    print("1. Try the prompts: Copy prompts/01_analyze_job.md to Claude/ChatGPT")
    print("2. Test automation: Run claude-code/setup_career_os.py interactively")
    print("3. Explore advanced: See advanced/README.md for full orchestrator")

if __name__ == "__main__":
    main()