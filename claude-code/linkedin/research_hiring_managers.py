#!/usr/bin/env python3
"""
LinkedIn Hiring Manager Research Helper
Helps research and document hiring managers and team members at target companies.

Usage: python research_hiring_managers.py
"""

import json
import csv
from pathlib import Path
from datetime import datetime

class HiringManagerResearch:
    def __init__(self):
        self.campaign_dir = Path("linkedin_campaigns")
        self.research_data = []

    def research_company(self):
        """Research a single company's team."""
        print("\n" + "="*70)
        print("Hiring Manager & Team Research")
        print("="*70)

        company_name = input("\nCompany name: ")
        role_title = input("Target role (e.g., 'Senior Product Manager'): ")

        print(f"\n--- Researching {company_name} ---")
        print("\nInstructions:")
        print("1. Go to LinkedIn and search: '{company_name} product manager'")
        print("2. Filter by 'People' and 'Current Company'")
        print("3. Document the key people below")

        team_data = {
            'company': company_name,
            'role': role_title,
            'researched_at': datetime.now().isoformat(),
            'hiring_manager': {},
            'team_members': [],
            'notes': {}
        }

        print("\n--- Hiring Manager ---")
        hm_name = input("Name (or leave blank if unknown): ")
        if hm_name:
            team_data['hiring_manager'] = {
                'name': hm_name,
                'title': input("Title: "),
                'linkedin_url': input("LinkedIn URL: "),
                'recent_post': input("Recent post topic (if any): "),
                'connection_strategy': input("How to connect? (e.g., 'Through mutual friend'): ")
            }

        print("\n--- Team Members ---")
        print("Add 5-7 team members to connect with (junior → senior)")

        num_members = int(input("\nHow many team members to add?: "))

        for i in range(num_members):
            print(f"\n  Member {i+1}:")
            member = {
                'name': input("    Name: "),
                'title': input("    Title: "),
                'seniority': input("    Seniority (Junior/Mid/Senior): "),
                'linkedin_url': input("    LinkedIn URL: "),
                'recent_activity': input("    Recent activity (post/project): "),
                'connection_priority': input("    Priority (1-5, 1=highest): ")
            }
            team_data['team_members'].append(member)

        # Sort by priority
        team_data['team_members'].sort(key=lambda x: int(x.get('connection_priority', 5)))

        print("\n--- Company Context ---")
        team_data['notes'] = {
            'recent_news': input("Recent company news/funding: "),
            'challenges': input("Challenges they're facing: "),
            'why_target': input("Why target this company?: "),
            'mutual_connections': input("Mutual connections (comma-separated): ")
        }

        self.research_data.append(team_data)
        self.save_research()

        print("\n✓ Research saved!")
        self.display_connection_plan(team_data)

    def display_connection_plan(self, team_data):
        """Display recommended connection plan."""
        print("\n" + "="*70)
        print(f"Connection Plan for {team_data['company']}")
        print("="*70)

        print("\n📅 Week 1:")
        junior_members = [m for m in team_data['team_members'] if m['seniority'].lower() == 'junior'][:2]
        for i, member in enumerate(junior_members, 1):
            print(f"  Day {i}: Connect with {member['name']} ({member['title']})")
            print(f"         Message angle: {member.get('recent_activity', 'Their work at company')}")

        print("\n📅 Week 2:")
        mid_members = [m for m in team_data['team_members'] if m['seniority'].lower() == 'mid'][:2]
        for i, member in enumerate(mid_members, 1):
            print(f"  Day {7+i}: Connect with {member['name']} ({member['title']})")

        if team_data['hiring_manager'].get('name'):
            print(f"\n📅 Week 3:")
            hm = team_data['hiring_manager']
            print(f"  Day 14: Connect with {hm['name']} ({hm['title']}) - Hiring Manager")
            print(f"          Strategy: {hm.get('connection_strategy', 'Personalized message')}")

        print("\n💡 Tips:")
        print("  - Space connections 2-3 days apart")
        print("  - Comment on their posts before connecting")
        print("  - Personalize every message")
        print("  - Track all interactions in tracking.csv")

    def save_research(self):
        """Save research to file."""
        output_dir = self.campaign_dir / "research"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"research_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(self.research_data, f, indent=2)

        # Also save to CSV for easy tracking
        csv_file = output_dir / f"research_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Company', 'Name', 'Title', 'Seniority', 'LinkedIn URL',
                'Recent Activity', 'Priority', 'Role'
            ])

            for company_data in self.research_data:
                company = company_data['company']

                # Add hiring manager
                if company_data['hiring_manager'].get('name'):
                    hm = company_data['hiring_manager']
                    writer.writerow([
                        company, hm['name'], hm['title'], 'Manager',
                        hm['linkedin_url'], hm.get('recent_post', ''),
                        '1', 'Hiring Manager'
                    ])

                # Add team members
                for member in company_data['team_members']:
                    writer.writerow([
                        company, member['name'], member['title'],
                        member['seniority'], member['linkedin_url'],
                        member.get('recent_activity', ''),
                        member.get('connection_priority', '5'), 'Team Member'
                    ])

        print(f"\n✓ Research saved to: {output_file}")
        print(f"✓ CSV saved to: {csv_file}")

    def run(self):
        """Run the research tool."""
        print("\n" + "="*70)
        print("LinkedIn Hiring Manager & Team Research")
        print("="*70)
        print("\nThis tool helps you research and document:")
        print("  • Hiring managers at target companies")
        print("  • Team members to connect with")
        print("  • Company context and challenges")
        print("  • Strategic connection plan\n")

        while True:
            print("\nOptions:")
            print("1. Research a company")
            print("2. View saved research")
            print("3. Exit")

            choice = input("\nChoice (1-3): ")

            if choice == '1':
                self.research_company()
            elif choice == '2':
                self.view_research()
            elif choice == '3':
                print("\n✓ Done! Use this research for your LinkedIn campaign.")
                break

    def view_research(self):
        """View saved research."""
        research_dir = self.campaign_dir / "research"
        if not research_dir.exists():
            print("\nNo research found yet. Research a company first!")
            return

        research_files = sorted(research_dir.glob("research_*.json"), reverse=True)
        if not research_files:
            print("\nNo research found yet.")
            return

        # Load most recent
        with open(research_files[0]) as f:
            data = json.load(f)

        print("\n" + "="*70)
        print("Saved Research")
        print("="*70)

        for company_data in data:
            print(f"\n📍 {company_data['company']}")
            print(f"   Role: {company_data['role']}")
            print(f"   Hiring Manager: {company_data['hiring_manager'].get('name', 'Unknown')}")
            print(f"   Team Members: {len(company_data['team_members'])}")
            print(f"   Researched: {company_data['researched_at'][:10]}")

def main():
    """Main entry point."""
    researcher = HiringManagerResearch()
    researcher.run()

if __name__ == "__main__":
    main()
