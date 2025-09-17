#!/usr/bin/env python3
"""
Career-OS Job Application Generator
End-to-end job application using Claude Code automation.

Usage: python apply_to_job.py --url [job-url]
       python apply_to_job.py --file [job-description.txt]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def main():
    """Main application flow."""
    parser = argparse.ArgumentParser(description="Generate job application materials")
    parser.add_argument("--url", help="Job posting URL")
    parser.add_argument("--file", help="Local job description file")
    parser.add_argument("--output", help="Output directory", default="user_data/applications")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    if not args.url and not args.file:
        print("❌ Please provide either --url or --file")
        sys.exit(1)

    print("🚀 Career-OS Job Application Generator")
    print("=" * 50)

    # Load user narrative
    narrative = load_user_narrative()
    if not narrative:
        print("❌ No narrative found. Run setup_career_os.py first.")
        sys.exit(1)

    # Get job description
    if args.url:
        job_data = scrape_job_posting(args.url)
    else:
        job_data = load_job_file(args.file)

    # Create output directory
    output_dir = create_output_directory(job_data, args.output)

    # Generate application materials
    print("\n📝 Generating application materials...")

    # Step 1: Job analysis
    print("🔍 Analyzing job posting...")
    job_analysis = analyze_job_with_prompts(job_data, narrative)
    save_analysis(job_analysis, output_dir)

    # Step 2: Generate resume
    print("📄 Generating tailored resume...")
    resume = generate_resume(job_data, narrative, job_analysis)
    save_resume(resume, output_dir)

    # Step 3: Generate cover letter
    print("✉️  Generating cover letter...")
    cover_letter = generate_cover_letter(job_data, narrative, job_analysis)
    save_cover_letter(cover_letter, output_dir)

    # Step 4: Quality review
    print("🔍 Running quality review...")
    quality_review = review_application_quality(job_data, resume, cover_letter, job_analysis)
    save_quality_review(quality_review, output_dir)

    # Summary
    print(f"\n✅ Application generated successfully!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📋 Files created:")
    print(f"  • job_analysis.md")
    print(f"  • resume.md")
    print(f"  • cover_letter.md")
    print(f"  • quality_review.md")
    print(f"\n📝 Next steps:")
    print(f"  1. Review quality_review.md for feedback")
    print(f"  2. Edit materials as needed")
    print(f"  3. Format for submission (PDF, etc.)")
    print(f"  4. Submit through company's application system")

def load_user_narrative():
    """Load user's professional narrative."""
    narrative_path = Path("user_data/narratives/main_narrative.json")
    if not narrative_path.exists():
        return None

    with open(narrative_path) as f:
        return json.load(f)

def scrape_job_posting(url):
    """Scrape job posting from URL."""
    print(f"🌐 Scraping job posting from {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract relevant content
        job_data = {
            "url": url,
            "title": extract_title(soup),
            "company": extract_company(soup),
            "description": extract_description(soup),
            "scraped_at": datetime.now().isoformat()
        }

        return job_data

    except Exception as e:
        print(f"❌ Error scraping job posting: {e}")
        print("💡 Try saving the job description to a file and using --file instead")
        sys.exit(1)

def extract_title(soup):
    """Extract job title from HTML."""
    # Common selectors for job titles
    selectors = [
        'h1',
        '.job-title',
        '.jobsearch-JobInfoHeader-title',
        '[data-testid="jobTitle"]'
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text().strip()

    return "Job Title Not Found"

def extract_company(soup):
    """Extract company name from HTML."""
    # Common selectors for company names
    selectors = [
        '.company-name',
        '.jobsearch-CompanyInfoContainer',
        '[data-testid="companyName"]'
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text().strip()

    return "Company Not Found"

def extract_description(soup):
    """Extract job description from HTML."""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text content
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text

def load_job_file(file_path):
    """Load job description from file."""
    print(f"📁 Loading job description from {file_path}")

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract basic info from filename or content
        job_data = {
            "url": f"file://{file_path}",
            "title": "Job Title from File",
            "company": "Company from File",
            "description": content,
            "loaded_at": datetime.now().isoformat()
        }

        return job_data

    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

def create_output_directory(job_data, base_output):
    """Create output directory for this application."""
    # Clean company and title for directory name
    company = clean_filename(job_data.get("company", "unknown"))
    title = clean_filename(job_data.get("title", "position"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    dir_name = f"{company}_{title}_{timestamp}"
    output_dir = Path(base_output) / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir

def clean_filename(text):
    """Clean text for use in filenames."""
    # Remove special characters and limit length
    clean = re.sub(r'[^\w\s-]', '', text)
    clean = re.sub(r'[-\s]+', '_', clean)
    return clean[:50].strip('_').lower()

def analyze_job_with_prompts(job_data, narrative):
    """Generate job analysis using prompt templates."""
    # This would integrate with Claude/ChatGPT API
    # For now, return structured template

    analysis = f"""# Job Analysis

## Job Posting
**Title**: {job_data['title']}
**Company**: {job_data['company']}
**URL**: {job_data['url']}

## Analysis Framework

### 1. What They Actually Want
[Analysis of hidden requirements based on job description]

### 2. Company Stage Signals
[What the language reveals about company maturity/culture]

### 3. Role Success Metrics
[How they'll measure performance in this role]

### 4. My Positioning Strategy
[How to frame background for maximum relevance]

### 5. Potential Concerns
[Gaps or mismatches to address proactively]

### 6. Unique Angle
[What makes me inevitable for this specific role]

---
*Generated by Career-OS on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    return analysis

def generate_resume(job_data, narrative, job_analysis):
    """Generate tailored resume."""
    personal = narrative["personal_info"]
    identity = narrative["professional_identity"]
    achievements = narrative["key_achievements"]

    resume = f"""# {personal['name']}
**{identity['level']}**

📧 {personal['email']} | 📱 {personal.get('phone', '')} | 📍 {personal['location']}
🔗 {personal.get('linkedin', '')} | 💻 {personal.get('github', '')}

## Professional Summary
{identity['positioning_statement']}

{identity['years_experience']} in {identity['domain_expertise']}, specializing in [relevant areas for this role].

## Core Competencies
• Product Management & Strategy
• Cross-functional Leadership
• Data-driven Decision Making
• [Additional skills relevant to role]

## Professional Experience

### {narrative['current_position']['title']}
**{narrative['current_position']['company']}** | {narrative['current_position']['start_date']} - {narrative['current_position']['end_date']} | {narrative['current_position']['location']}

• {achievements[0]['metric']} - {achievements[0]['context']}
• {achievements[1]['metric']} - {achievements[1]['context']}
• {achievements[2]['metric'] if len(achievements) > 2 else 'Additional achievement'}

## Education
[Education information]

## Technical Skills
**Product Tools**: {', '.join(narrative['technical_skills']['product_tools'])}
**Technical**: {', '.join(narrative['technical_skills']['technical_skills'])}
**Platforms**: {', '.join(narrative['technical_skills']['platforms'])}

---
*Tailored for {job_data['title']} at {job_data['company']}*
*Generated by Career-OS on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    return resume

def generate_cover_letter(job_data, narrative, job_analysis):
    """Generate tailored cover letter."""
    personal = narrative["personal_info"]

    cover_letter = f"""# Cover Letter

**{personal['name']}**
{personal['email']} | {personal['phone']}
{personal['location']}

{datetime.now().strftime('%B %d, %Y')}

Hiring Manager
{job_data['company']}

Dear Hiring Manager,

[Opening paragraph with specific relevance to the role]

[Body paragraph 1: Relevant experience addressing their primary need]

[Body paragraph 2: Unique value and cultural fit]

[Body paragraph 3: Future vision and approach to the role]

[Closing paragraph: Professional and confident close]

Sincerely,
{personal['name']}

---
*Generated by Career-OS on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    return cover_letter

def review_application_quality(job_data, resume, cover_letter, job_analysis):
    """Generate quality review of application materials."""
    review = f"""# Application Quality Review

## Job Application Summary
**Position**: {job_data['title']}
**Company**: {job_data['company']}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Quality Assessment

### 1. Relevance Assessment (Score: __/10)
- [ ] Key requirements addressed
- [ ] Language appropriately mirrored
- [ ] Positioning feels inevitable
- [ ] No obvious gaps or mismatches

### 2. Authenticity Check (Score: __/10)
- [ ] Feels specific to this role/company
- [ ] Achievements believable and verifiable
- [ ] Voice genuine, not templated
- [ ] Enthusiasm authentic

### 3. Professional Standards
**Resume Technical Check:**
- [ ] Clean, scannable format
- [ ] Consistent formatting
- [ ] No typos or errors
- [ ] Appropriate length
- [ ] ATS-friendly structure

**Cover Letter Quality:**
- [ ] Proper business format
- [ ] 250-400 word count
- [ ] Company/role details accurate
- [ ] Professional tone throughout
- [ ] Strong opening and closing

### 4. Competitive Positioning
**Strengths:**
- [What makes this application memorable]

**Areas for Improvement:**
- [Specific suggestions for enhancement]

### 5. Final Recommendation
- [ ] Submit as-is
- [ ] Minor tweaks needed
- [ ] Major revision required
- [ ] Wrong fit - consider skipping

**Interview Probability**: Low / Medium / High

**Next Steps:**
1. [Specific action items]
2. [Timeline for revisions]
3. [Additional research needed]

---
*Generated by Career-OS Quality Review System*
"""

    return review

def save_analysis(analysis, output_dir):
    """Save job analysis to file."""
    with open(output_dir / "job_analysis.md", "w") as f:
        f.write(analysis)

def save_resume(resume, output_dir):
    """Save resume to file."""
    with open(output_dir / "resume.md", "w") as f:
        f.write(resume)

def save_cover_letter(cover_letter, output_dir):
    """Save cover letter to file."""
    with open(output_dir / "cover_letter.md", "w") as f:
        f.write(cover_letter)

def save_quality_review(review, output_dir):
    """Save quality review to file."""
    with open(output_dir / "quality_review.md", "w") as f:
        f.write(review)

if __name__ == "__main__":
    main()