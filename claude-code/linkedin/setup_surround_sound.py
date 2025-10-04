#!/usr/bin/env python3
"""
LinkedIn Surround Sound Campaign Setup
Interactive script to build a 2-week LinkedIn presence campaign for target companies.

Usage: python setup_surround_sound.py
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import csv

class SurroundSoundSetup:
    def __init__(self):
        self.campaign_dir = Path("linkedin_campaigns")
        self.campaign_dir.mkdir(exist_ok=True)
        self.campaign_data = {}

    def welcome(self):
        """Welcome message and overview."""
        print("\n" + "="*70)
        print("LinkedIn Surround Sound Campaign Setup")
        print("="*70)
        print("\nThis tool will help you build a 2-week LinkedIn presence campaign")
        print("to get noticed by target companies BEFORE you apply.\n")
        print("We'll create:")
        print("  ✓ Target company map with key people")
        print("  ✓ 2-week content calendar")
        print("  ✓ Connection request messages")
        print("  ✓ Engagement tracking spreadsheet")
        print("\nThis takes about 15-20 minutes. Let's get started!\n")
        input("Press Enter to continue...")

    def gather_user_info(self):
        """Gather user background information."""
        print("\n" + "-"*70)
        print("Step 1: Your Background")
        print("-"*70)

        self.campaign_data['user'] = {
            'name': input("\nYour name: "),
            'current_role': input("Current/recent role: "),
            'expertise': input("Key expertise areas (comma-separated): "),
            'top_achievement': input("Your most impressive metric (e.g., '$400K saved', '70% retention'): "),
            'years_experience': input("Years of experience: "),
            'unique_value': input("What makes you different from other candidates: ")
        }

        print("\n✓ Got it! Now let's identify your target companies.")

    def gather_target_companies(self):
        """Gather target company information."""
        print("\n" + "-"*70)
        print("Step 2: Target Companies")
        print("-"*70)
        print("\nHow many companies do you want to target? (Recommended: 5-10)")
        num_companies = int(input("Number of companies: "))

        self.campaign_data['companies'] = []

        for i in range(num_companies):
            print(f"\n--- Company {i+1} ---")
            company = {
                'name': input("Company name: "),
                'stage': input("Company stage (Startup/Growth/Public): "),
                'hiring_manager': input("Hiring manager name (if known, or leave blank): "),
                'challenge': input("What challenge are they facing? (from news/job postings): "),
                'why_target': input("Why this company for you?: ")
            }
            self.campaign_data['companies'].append(company)

        print(f"\n✓ Added {num_companies} target companies!")

    def define_goals(self):
        """Define campaign goals and timeline."""
        print("\n" + "-"*70)
        print("Step 3: Campaign Goals")
        print("-"*70)

        print("\nWhat's your primary goal?")
        print("1. Build presence before applying (2-3 weeks)")
        print("2. Already applied, want to follow up (1 week)")
        print("3. Long-term relationship building (4+ weeks)")

        goal_choice = input("\nChoice (1-3): ")

        goals_map = {
            '1': {
                'type': 'pre_application',
                'timeline': '2-3 weeks',
                'focus': 'Build recognition through content and engagement'
            },
            '2': {
                'type': 'post_application',
                'timeline': '1 week',
                'focus': 'Stay top-of-mind with value-adds'
            },
            '3': {
                'type': 'long_term',
                'timeline': '4+ weeks',
                'focus': 'Establish thought leadership in domain'
            }
        }

        self.campaign_data['goals'] = goals_map.get(goal_choice, goals_map['1'])

        print(f"\n✓ Goal set: {self.campaign_data['goals']['focus']}")

    def generate_calendar(self):
        """Generate 2-week content calendar."""
        print("\n" + "-"*70)
        print("Step 4: Generating Content Calendar")
        print("-"*70)
        print("\nCreating your 2-week content calendar...\n")

        # Generate calendar based on best practices
        start_date = datetime.now()
        calendar = []

        # Week 1
        calendar.append({
            'day': 1,
            'date': (start_date + timedelta(days=0)).strftime('%Y-%m-%d'),
            'day_name': 'Monday',
            'type': 'post',
            'action': 'Pattern Recognition Post',
            'description': 'Share pattern observed across multiple experiences',
            'best_time': '10:00 AM',
            'companies': 'All',
            'estimated_time': '30 mins to draft'
        })

        calendar.append({
            'day': 2,
            'date': (start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
            'day_name': 'Tuesday',
            'type': 'engage',
            'action': 'Strategic Engagement',
            'description': 'Connect with 2 junior team members, comment on 1 post',
            'companies': self.campaign_data['companies'][0]['name'] if self.campaign_data['companies'] else 'Target Company 1',
            'estimated_time': '20 mins'
        })

        calendar.append({
            'day': 3,
            'date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
            'day_name': 'Wednesday',
            'type': 'post',
            'action': 'Failure Story Post',
            'description': 'Share a mistake and what you learned',
            'best_time': '9:30 AM',
            'companies': 'All',
            'estimated_time': '30 mins to draft'
        })

        calendar.append({
            'day': 4,
            'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
            'day_name': 'Thursday',
            'type': 'engage',
            'action': 'Thought Leader Engagement',
            'description': 'Comment on 3 thought leader posts (Lenny, etc.)',
            'companies': 'Industry visibility',
            'estimated_time': '15 mins'
        })

        calendar.append({
            'day': 5,
            'date': (start_date + timedelta(days=4)).strftime('%Y-%m-%d'),
            'day_name': 'Friday',
            'type': 'post',
            'action': 'Framework Share',
            'description': 'Share a framework or process you use',
            'best_time': '10:30 AM',
            'companies': 'All',
            'estimated_time': '30 mins to draft'
        })

        # Weekend
        calendar.append({
            'day': 6,
            'date': (start_date + timedelta(days=5)).strftime('%Y-%m-%d'),
            'day_name': 'Saturday',
            'type': 'research',
            'action': 'Weekend Research',
            'description': 'Review engagement metrics, plan Week 2',
            'estimated_time': '30 mins'
        })

        # Week 2
        calendar.append({
            'day': 8,
            'date': (start_date + timedelta(days=7)).strftime('%Y-%m-%d'),
            'day_name': 'Monday',
            'type': 'post',
            'action': 'Industry Trend Post',
            'description': 'Comment on industry trend with your perspective',
            'best_time': '10:00 AM',
            'companies': 'All',
            'estimated_time': '30 mins to draft'
        })

        calendar.append({
            'day': 9,
            'date': (start_date + timedelta(days=8)).strftime('%Y-%m-%d'),
            'day_name': 'Tuesday',
            'type': 'engage',
            'action': 'Mid-Level Connections',
            'description': 'Connect with 2 mid-level PMs',
            'companies': self.campaign_data['companies'][1]['name'] if len(self.campaign_data['companies']) > 1 else 'Target Company 2',
            'estimated_time': '20 mins'
        })

        calendar.append({
            'day': 10,
            'date': (start_date + timedelta(days=9)).strftime('%Y-%m-%d'),
            'day_name': 'Wednesday',
            'type': 'post',
            'action': 'Case Study Post',
            'description': 'Deep dive on specific project with results',
            'best_time': '9:30 AM',
            'companies': self.campaign_data['companies'][0]['name'] if self.campaign_data['companies'] else 'Target Company 1',
            'estimated_time': '45 mins to draft'
        })

        calendar.append({
            'day': 11,
            'date': (start_date + timedelta(days=10)).strftime('%Y-%m-%d'),
            'day_name': 'Thursday',
            'type': 'engage',
            'action': 'Senior Connections',
            'description': 'Connect with 1-2 senior PMs or hiring managers',
            'companies': 'Top 2 companies',
            'estimated_time': '30 mins (personalized messages)'
        })

        calendar.append({
            'day': 12,
            'date': (start_date + timedelta(days=11)).strftime('%Y-%m-%d'),
            'day_name': 'Friday',
            'type': 'post',
            'action': 'Tool/Process Share',
            'description': 'Share a tool or process that works',
            'best_time': '10:30 AM',
            'companies': 'All',
            'estimated_time': '30 mins to draft'
        })

        calendar.append({
            'day': 13,
            'date': (start_date + timedelta(days=12)).strftime('%Y-%m-%d'),
            'day_name': 'Saturday',
            'type': 'review',
            'action': 'Campaign Review',
            'description': 'Review metrics, prepare for applications',
            'estimated_time': '1 hour'
        })

        calendar.append({
            'day': 14,
            'date': (start_date + timedelta(days=13)).strftime('%Y-%m-%d'),
            'day_name': 'Sunday',
            'type': 'apply',
            'action': 'Application Day',
            'description': 'Submit applications to top 3 companies',
            'companies': 'Top 3 companies',
            'estimated_time': '2-3 hours (review + submit)'
        })

        self.campaign_data['calendar'] = calendar

        print("✓ Content calendar created!")
        print(f"   - {len([c for c in calendar if c['type'] == 'post'])} posts scheduled")
        print(f"   - {len([c for c in calendar if c['type'] == 'engage'])} engagement days")
        print(f"   - Total time commitment: ~20 mins/day\n")

    def create_tracking_file(self):
        """Create tracking spreadsheet."""
        print("\n" + "-"*70)
        print("Step 5: Creating Tracking Files")
        print("-"*70)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        campaign_folder = self.campaign_dir / f"campaign_{timestamp}"
        campaign_folder.mkdir(exist_ok=True)

        # Create tracking CSV
        tracking_file = campaign_folder / "tracking.csv"
        with open(tracking_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Company', 'Hiring Manager', 'Connection Date', 'Touchpoints',
                'Last Interaction', 'Interaction Type', 'Application Date',
                'Response (Y/N)', 'Interview Date', 'Status', 'Notes'
            ])

            for company in self.campaign_data['companies']:
                writer.writerow([
                    company['name'],
                    company.get('hiring_manager', ''),
                    '', '0', '', '', '', 'N', '', 'Target Identified', ''
                ])

        # Create calendar CSV
        calendar_file = campaign_folder / "content_calendar.csv"
        with open(calendar_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'day', 'date', 'day_name', 'type', 'action', 'description',
                'best_time', 'companies', 'estimated_time', 'status', 'notes'
            ])
            writer.writeheader()

            for item in self.campaign_data['calendar']:
                item['status'] = 'Pending'
                item['notes'] = ''
                if 'best_time' not in item:
                    item['best_time'] = ''
                writer.writerow(item)

        # Save campaign configuration
        config_file = campaign_folder / "campaign_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.campaign_data, f, indent=2)

        print(f"\n✓ Campaign files created in: {campaign_folder}")
        print(f"   - tracking.csv: Track all interactions")
        print(f"   - content_calendar.csv: Your 2-week schedule")
        print(f"   - campaign_config.json: Campaign configuration\n")

        return campaign_folder

    def print_next_steps(self, campaign_folder):
        """Print next steps for user."""
        print("\n" + "="*70)
        print("Setup Complete! Here's What to Do Next:")
        print("="*70)

        print("\n📋 Immediate Actions:")
        print("  1. Open tracking.csv to add hiring manager details")
        print("  2. Review content_calendar.csv for your schedule")
        print("  3. Use the LinkedIn prompts to generate specific content:")
        print("     - prompts/linkedin/06_map_target_companies.md")
        print("     - prompts/linkedin/07_generate_content_calendar.md")

        print("\n📅 Week 1 Kickoff (Start Tomorrow):")
        day1 = self.campaign_data['calendar'][0]
        print(f"  Day 1 ({day1['date']}): {day1['action']}")
        print(f"  - {day1['description']}")
        print(f"  - Estimated time: {day1.get('estimated_time', '30 mins')}")

        print("\n🎯 Daily Routine (20 mins total):")
        print("  Morning (5 mins): Check LinkedIn, like 3 strategic posts")
        print("  Lunch (10 mins): Write 1 comment, send 2 connections")
        print("  Evening (5 mins): Review metrics, plan tomorrow")

        print("\n📊 Success Metrics to Track:")
        print("  - Profile views from target companies: 30+ weekly")
        print("  - Connection acceptance rate: 70%+")
        print("  - Post engagement: 2-3 comments from targets")
        print("  - Recognition: 'I've seen your posts' in interviews")

        print("\n💡 Pro Tips:")
        print("  - Post on Tue/Wed/Thu between 9-11 AM EST")
        print("  - Comment within first hour of thought leader posts")
        print("  - Personalize every connection request")
        print("  - Track everything in tracking.csv")
        print("  - Review metrics weekly, adjust strategy")

        print(f"\n📁 Your campaign folder: {campaign_folder}")
        print("\n🚀 Ready to build your surround sound presence!")
        print("="*70 + "\n")

    def run(self):
        """Run the complete setup process."""
        self.welcome()
        self.gather_user_info()
        self.gather_target_companies()
        self.define_goals()
        self.generate_calendar()
        campaign_folder = self.create_tracking_file()
        self.print_next_steps(campaign_folder)

def main():
    """Main entry point."""
    setup = SurroundSoundSetup()
    setup.run()

if __name__ == "__main__":
    main()
