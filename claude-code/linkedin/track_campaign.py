#!/usr/bin/env python3
"""
LinkedIn Campaign Tracker
Track interactions, measure success metrics, and analyze campaign performance.

Usage: python track_campaign.py
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

class CampaignTracker:
    def __init__(self):
        self.campaign_dir = Path("linkedin_campaigns")
        self.tracking_file = None
        self.load_tracking_file()

    def load_tracking_file(self):
        """Find and load the tracking file."""
        # Find most recent campaign
        if self.campaign_dir.exists():
            campaigns = sorted(self.campaign_dir.glob("campaign_*"), reverse=True)
            if campaigns:
                tracking = campaigns[0] / "tracking.csv"
                if tracking.exists():
                    self.tracking_file = tracking
                    print(f"✓ Loaded tracking file: {tracking}")
                    return

        print("⚠️  No tracking file found. Run setup_surround_sound.py first.")

    def log_interaction(self):
        """Log a new interaction."""
        if not self.tracking_file:
            print("No tracking file found!")
            return

        print("\n--- Log New Interaction ---")
        company = input("Company name: ")
        interaction_type = input("Interaction type (connection/comment/like/email/call/inmail): ")
        notes = input("Notes (optional): ")

        # Load existing data
        rows = []
        with open(self.tracking_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Company'] == company:
                    # Update this row
                    current_touchpoints = int(row['Touchpoints'] or 0)
                    row['Touchpoints'] = str(current_touchpoints + 1)
                    row['Last Interaction'] = datetime.now().strftime('%Y-%m-%d')
                    row['Interaction Type'] = interaction_type
                    if notes:
                        row['Notes'] = row.get('Notes', '') + f" | {notes}"
                rows.append(row)

        # Write back
        with open(self.tracking_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✓ Logged {interaction_type} interaction with {company}")

    def view_metrics(self):
        """Display campaign metrics."""
        if not self.tracking_file:
            print("No tracking file found!")
            return

        with open(self.tracking_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        print("\n" + "="*70)
        print("Campaign Metrics")
        print("="*70)

        # Overall stats
        total_companies = len(data)
        total_touchpoints = sum(int(row['Touchpoints'] or 0) for row in data)
        applied = sum(1 for row in data if row['Application Date'])
        responses = sum(1 for row in data if row['Response (Y/N)'] == 'Y')
        interviews = sum(1 for row in data if row['Interview Date'])

        print(f"\n📊 Overall Stats:")
        print(f"   Target Companies: {total_companies}")
        print(f"   Total Touchpoints: {total_touchpoints}")
        print(f"   Average per Company: {total_touchpoints/total_companies:.1f}")
        print(f"   Applications Submitted: {applied}")
        print(f"   Responses Received: {responses}")
        print(f"   Interviews Scheduled: {interviews}")

        if applied > 0:
            response_rate = (responses / applied) * 100
            interview_rate = (interviews / applied) * 100
            print(f"\n📈 Conversion Rates:")
            print(f"   Response Rate: {response_rate:.1f}% (Target: 15-20%)")
            print(f"   Interview Rate: {interview_rate:.1f}% (Target: 10-15%)")

        # Touchpoint analysis
        interaction_types = []
        for row in data:
            if row['Interaction Type']:
                interaction_types.append(row['Interaction Type'])

        if interaction_types:
            print(f"\n🔄 Interaction Breakdown:")
            type_counts = Counter(interaction_types)
            for itype, count in type_counts.most_common():
                print(f"   {itype}: {count}")

        # Company status
        print(f"\n🎯 Company Status:")
        status_counts = Counter(row['Status'] for row in data if row['Status'])
        for status, count in status_counts.most_common():
            print(f"   {status}: {count}")

        # Success tips
        print(f"\n💡 Analysis:")
        if total_touchpoints / total_companies < 3:
            print("   ⚠️  Low touchpoint average. Aim for 5-7 before applying.")
        if applied > 0 and response_rate < 15:
            print("   ⚠️  Low response rate. Are you warming up enough?")
        if total_touchpoints / total_companies >= 5:
            print("   ✅ Good engagement level!")
        if responses > 0 and response_rate >= 15:
            print("   ✅ Response rate looks healthy!")

    def show_next_actions(self):
        """Show recommended next actions."""
        if not self.tracking_file:
            print("No tracking file found!")
            return

        with open(self.tracking_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        print("\n" + "="*70)
        print("Recommended Next Actions")
        print("="*70)

        # Find companies that need attention
        needs_attention = []
        ready_to_apply = []
        waiting_response = []

        for row in data:
            touchpoints = int(row['Touchpoints'] or 0)
            company = row['Company']
            status = row['Status']

            if touchpoints == 0:
                needs_attention.append((company, "Start engagement"))
            elif touchpoints < 3:
                needs_attention.append((company, f"Only {touchpoints} touchpoints - need more"))
            elif touchpoints >= 5 and not row['Application Date']:
                ready_to_apply.append(company)
            elif row['Application Date'] and not row['Response (Y/N)']:
                days_since = (datetime.now() - datetime.fromisoformat(row['Application Date'])).days
                waiting_response.append((company, days_since))

        if needs_attention:
            print("\n⚠️  Companies Needing Engagement:")
            for company, reason in needs_attention[:5]:
                print(f"   • {company}: {reason}")

        if ready_to_apply:
            print("\n✅ Ready to Apply (5+ touchpoints):")
            for company in ready_to_apply[:5]:
                print(f"   • {company}")

        if waiting_response:
            print("\n⏳ Waiting for Response:")
            for company, days in waiting_response[:5]:
                print(f"   • {company} ({days} days since application)")
                if days >= 7:
                    print(f"      → Consider follow-up")

    def run(self):
        """Run the tracker."""
        if not self.tracking_file:
            print("\n⚠️  No campaign found. Run setup_surround_sound.py first!")
            return

        while True:
            print("\n" + "="*70)
            print("LinkedIn Campaign Tracker")
            print("="*70)
            print("\nOptions:")
            print("1. Log new interaction")
            print("2. View metrics")
            print("3. Show next actions")
            print("4. Export report")
            print("5. Exit")

            choice = input("\nChoice (1-5): ")

            if choice == '1':
                self.log_interaction()
            elif choice == '2':
                self.view_metrics()
            elif choice == '3':
                self.show_next_actions()
            elif choice == '4':
                self.export_report()
            elif choice == '5':
                print("\n✓ Keep tracking your campaign!")
                break

    def export_report(self):
        """Export campaign report."""
        if not self.tracking_file:
            return

        report_file = self.tracking_file.parent / f"report_{datetime.now().strftime('%Y%m%d')}.txt"

        with open(report_file, 'w') as f:
            f.write("LinkedIn Surround Sound Campaign Report\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

            # Add metrics (reuse view_metrics logic)
            # Simplified for now
            f.write("See metrics in terminal via 'View metrics' option.\n")

        print(f"\n✓ Report exported to: {report_file}")

def main():
    """Main entry point."""
    tracker = CampaignTracker()
    tracker.run()

if __name__ == "__main__":
    main()
