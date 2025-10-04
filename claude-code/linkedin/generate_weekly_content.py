#!/usr/bin/env python3
"""
Weekly LinkedIn Content Generator
Generates posts, comments, and connection messages for your LinkedIn campaign.

Usage: python generate_weekly_content.py [--week 1|2]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

# Content templates from the knowledge base
CONTENT_TEMPLATES = {
    'pattern_recognition': """[{num}] companies. Same mistake. Different outcomes.

Company 1: {approach1} → {result1}
Company 2: {approach2} → {result2}
Company 3: {approach3} → {result3}

The pattern: {insight}
The lesson: {takeaway}

What patterns have you seen?""",

    'failure_story': """Biggest {role} mistake: {belief}

They wanted: {request}
We built: {solution}
Result: {negative_outcome}

What worked instead: {actual_solution}
Lesson: {insight}""",

    'framework': """My '{framework_name}' framework for {problem}:

1. {step1}
2. {step2}
3. {step3}
4. {step4}

Used this to {impact}.

What frameworks have worked for you?""",

    'counterintuitive': """Everyone thinks {common_belief}.

The data says otherwise.

We analyzed {data_points} and found:
- {finding1}
- {finding2}
- {finding3}

The lesson: {insight}""",

    'case_study': """Case study: {project_name}

Challenge: {problem}
Approach: {solution}
Result: {outcome}

What worked:
- {success1}
- {success2}

What didn't:
- {failure1}

Key lesson: {insight}"""
}

COMMENT_FORMULAS = {
    'data_drop': """This aligns with something we found at {your_company}.  We analyzed {data_points} and saw {pattern}.

The breakthrough: {insight}

Have you found {question}?""",

    'pattern_recognition': """{num} times I've seen this pattern across {domain}.

At {company1}: {approach} → {result}
At {company2}: {different_approach} → {different_result}

The common thread: {insight}

Thoughts?""",

    'vulnerability': """Made this exact mistake at {your_company}.

Thought {belief}. Built {solution}.
Result: {negative_outcome}.

What actually worked: {corrected_approach}, which got us {positive_result}.

Your post nails why {their_insight}."""
}

CONNECTION_TEMPLATES = {
    'recent_post': """Hi {name},

Your post about {topic} really resonated. At {your_company}, we faced similar challenges with {context}. Would love to connect and hear more about your approach.

{your_name}""",

    'project_specific': """Hi {name},

Really impressed by {company}'s work on {project}. At {your_company}, I led similar initiatives and achieved {result}. Would love to connect and learn more.

{your_name}""",

    'shared_challenge': """Hi {name},

Saw you're working on {challenge} at {company}. I tackled the same at {your_company} and found {approach} helped. Happy to compare notes!

{your_name}""",

    'mutual_connection': """Hi {name},

{mutual} mentioned your work on {project} at {company}. I've been working on similar challenges in {domain} and would love to connect.

{your_name}"""
}

class ContentGenerator:
    def __init__(self):
        self.user_profile = self.load_user_profile()

    def load_user_profile(self):
        """Load user profile from campaign config."""
        # Try to find most recent campaign
        campaign_dir = Path("linkedin_campaigns")
        if campaign_dir.exists():
            campaigns = sorted(campaign_dir.glob("campaign_*"), reverse=True)
            if campaigns:
                config_file = campaigns[0] / "campaign_config.json"
                if config_file.exists():
                    with open(config_file) as f:
                        config = json.load(f)
                        return config.get('user', {})

        # If no campaign found, prompt for basic info
        print("\nNo campaign found. Let's set up your basic profile:")
        return {
            'name': input("Your name: "),
            'current_role': input("Current role: "),
            'expertise': input("Key expertise: "),
            'top_achievement': input("Top achievement: ")
        }

    def generate_pattern_post(self):
        """Generate a pattern recognition post."""
        print("\n--- Generate Pattern Recognition Post ---")
        print("This post shares patterns you've observed across multiple experiences.\n")

        num = input("How many companies/projects? (e.g., 3): ")
        print(f"\nFor each of the {num} examples, provide:")

        examples = []
        for i in range(int(num)):
            print(f"\nExample {i+1}:")
            approach = input(f"  Approach taken: ")
            result = input(f"  Result (with metric): ")
            examples.append((approach, result))

        insight = input("\nWhat's the pattern you observed?: ")
        takeaway = input("What's the lesson?: ")

        # Fill template
        post = f"[{num}] companies. Same pattern. Different approaches.\n\n"
        for i, (approach, result) in enumerate(examples, 1):
            post += f"Company {i}: {approach} → {result}\n"

        post += f"\nThe pattern: {insight}\n"
        post += f"The lesson: {takeaway}\n\n"
        post += "What patterns have you seen?"

        return {
            'type': 'Pattern Recognition',
            'post': post,
            'best_time': 'Monday, 10:00 AM',
            'hashtags': '#ProductManagement #Lessons #Strategy',
            'engagement_tip': 'Ask for others\' patterns to drive comments'
        }

    def generate_failure_post(self):
        """Generate a failure story post."""
        print("\n--- Generate Failure Story Post ---")
        print("Share a mistake and what you learned from it.\n")

        role = self.user_profile.get('current_role', 'PM')
        belief = input("What was the mistaken belief?: ")
        request = input("What did users/stakeholders want?: ")
        solution = input("What did you build?: ")
        negative_outcome = input("What was the result? (with metric): ")
        actual_solution = input("What worked instead?: ")
        insight = input("What's the lesson?: ")

        post = f"Biggest {role} mistake: {belief}\n\n"
        post += f"They wanted: {request}\n"
        post += f"We built: {solution}\n"
        post += f"Result: {negative_outcome}\n\n"
        post += f"What worked instead: {actual_solution}\n"
        post += f"Lesson: {insight}"

        return {
            'type': 'Failure Story',
            'post': post,
            'best_time': 'Wednesday, 9:30 AM',
            'hashtags': '#ProductLessons #FailureStories #Growth',
            'engagement_tip': 'Vulnerability builds trust—people will relate'
        }

    def generate_framework_post(self):
        """Generate a framework share post."""
        print("\n--- Generate Framework Post ---")
        print("Share a framework or process you use.\n")

        framework_name = input("Framework name: ")
        problem = input("What problem does it solve?: ")

        print("\nEnter 4 steps for your framework:")
        steps = []
        for i in range(4):
            step = input(f"  Step {i+1}: ")
            steps.append(step)

        impact = input("\nWhat impact did it have? (with metric): ")

        post = f"My '{framework_name}' framework for {problem}:\n\n"
        for i, step in enumerate(steps, 1):
            post += f"{i}. {step}\n"

        post += f"\nUsed this to {impact}.\n\n"
        post += "What frameworks have worked for you?"

        return {
            'type': 'Framework Share',
            'post': post,
            'best_time': 'Friday, 10:30 AM',
            'hashtags': '#ProductManagement #Framework #Process',
            'engagement_tip': 'People love actionable frameworks—offer to share details'
        }

    def generate_comment(self):
        """Generate a strategic comment."""
        print("\n--- Generate Strategic Comment ---")
        print("Create a comment that demonstrates expertise.\n")

        print("What strategy do you want to use?")
        print("1. Data Drop (add specific data)")
        print("2. Pattern Recognition (connect to broader pattern)")
        print("3. Vulnerability (share related failure)")

        choice = input("\nChoice (1-3): ")

        your_company = self.user_profile.get('current_role', 'my company').split(' at ')[-1] if ' at ' in self.user_profile.get('current_role', '') else '[YOUR_COMPANY]'

        if choice == '1':
            print("\nData Drop Strategy:")
            data_points = input("How much data did you analyze? (e.g., '375K transactions'): ")
            pattern = input("What pattern did you see?: ")
            insight = input("What was the breakthrough?: ")
            question = input("What question to ask them?: ")

            comment = f"This aligns with something we found at {your_company}. We analyzed {data_points} and saw {pattern}.\n\n"
            comment += f"The breakthrough: {insight}\n\n"
            comment += f"Have you found {question}?"

        elif choice == '2':
            print("\nPattern Recognition Strategy:")
            num = input("How many times have you seen this? (e.g., '3'): ")
            domain = input("In what domain? (e.g., 'marketplaces'): ")

            examples = []
            for i in range(2):
                approach = input(f"\nExample {i+1} approach: ")
                result = input(f"Example {i+1} result: ")
                examples.append((approach, result))

            insight = input("\nWhat's the common thread?: ")

            comment = f"[{num}] times I've seen this pattern across {domain}.\n\n"
            for i, (approach, result) in enumerate(examples, 1):
                company_placeholder = f"Company {chr(64+i)}"
                comment += f"At {company_placeholder}: {approach} → {result}\n"
            comment += f"\nThe common thread: {insight}\n\nThoughts?"

        else:  # Vulnerability
            print("\nVulnerability Strategy:")
            belief = input("What did you mistakenly think?: ")
            solution = input("What did you build?: ")
            negative_outcome = input("What was the result?: ")
            corrected_approach = input("What worked instead?: ")
            positive_result = input("What was the positive outcome?: ")

            comment = f"Made this exact mistake at {your_company}.\n\n"
            comment += f"Thought {belief}. Built {solution}.\n"
            comment += f"Result: {negative_outcome}.\n\n"
            comment += f"What actually worked: {corrected_approach}, which got us {positive_result}.\n\n"
            comment += "Your post nails this!"

        return {
            'type': 'Strategic Comment',
            'comment': comment,
            'when_to_use': 'Within first hour of post for max visibility',
            'follow_up': 'If they respond, offer to share more details'
        }

    def generate_connection_message(self):
        """Generate a connection request message."""
        print("\n--- Generate Connection Message ---")
        print("Create a personalized connection request.\n")

        name = input("Their first name: ")
        topic = input("What post/project of theirs to reference?: ")
        your_context = input("Your relevant experience/context: ")
        your_name = self.user_profile.get('name', '[YOUR_NAME]')

        message = f"Hi {name},\n\n"
        message += f"Your post about {topic} really resonated. At {your_context}. "
        message += f"Would love to connect and hear more about your approach.\n\n"
        message += f"{your_name}"

        return {
            'type': 'Connection Request',
            'message': message,
            'character_count': len(message),
            'tip': 'LinkedIn limit is 300 characters—this is within limit' if len(message) <= 300 else 'WARNING: Over 300 characters, please shorten',
            'follow_up': 'Day 1: Thank them, Day 3-5: Like their post, Day 7-10: Share resource'
        }

    def save_content(self, content_items):
        """Save generated content to file."""
        output_dir = Path("linkedin_campaigns") / "generated_content"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"content_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'user': self.user_profile.get('name', 'Unknown'),
                'content': content_items
            }, f, indent=2)

        print(f"\n✓ Content saved to: {output_file}")
        return output_file

    def run_interactive(self):
        """Run interactive content generation."""
        print("\n" + "="*70)
        print("LinkedIn Content Generator")
        print("="*70)
        print("\nGenerate posts, comments, and connection messages for your campaign.\n")

        content_items = []

        while True:
            print("\nWhat would you like to generate?")
            print("1. Pattern Recognition Post")
            print("2. Failure Story Post")
            print("3. Framework Post")
            print("4. Strategic Comment")
            print("5. Connection Message")
            print("6. Save and Exit")

            choice = input("\nChoice (1-6): ")

            if choice == '1':
                content = self.generate_pattern_post()
                content_items.append(content)
                self.display_content(content)
            elif choice == '2':
                content = self.generate_failure_post()
                content_items.append(content)
                self.display_content(content)
            elif choice == '3':
                content = self.generate_framework_post()
                content_items.append(content)
                self.display_content(content)
            elif choice == '4':
                content = self.generate_comment()
                content_items.append(content)
                self.display_content(content)
            elif choice == '5':
                content = self.generate_connection_message()
                content_items.append(content)
                self.display_content(content)
            elif choice == '6':
                if content_items:
                    self.save_content(content_items)
                print("\n✓ Done! Use this content in your LinkedIn campaign.")
                break

    def display_content(self, content):
        """Display generated content in a nice format."""
        print("\n" + "="*70)
        print(f"Generated: {content['type']}")
        print("="*70)

        if 'post' in content:
            print("\n📝 Post Content:\n")
            print(content['post'])
            print(f"\n⏰ Best Time: {content.get('best_time', 'N/A')}")
            print(f"🏷️  Hashtags: {content.get('hashtags', 'N/A')}")
            print(f"💡 Tip: {content.get('engagement_tip', 'N/A')}")

        elif 'comment' in content:
            print("\n💬 Comment:\n")
            print(content['comment'])
            print(f"\n⏰ When: {content.get('when_to_use', 'N/A')}")
            print(f"🔄 Follow-up: {content.get('follow_up', 'N/A')}")

        elif 'message' in content:
            print("\n🤝 Connection Message:\n")
            print(content['message'])
            print(f"\n📊 Length: {content.get('character_count', 0)} characters")
            print(f"✅ {content.get('tip', '')}")
            print(f"🔄 Follow-up: {content.get('follow_up', 'N/A')}")

        print("\n" + "="*70)
        input("\nPress Enter to continue...")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate LinkedIn content')
    parser.add_argument('--batch', action='store_true', help='Generate full week of content')
    args = parser.parse_args()

    generator = ContentGenerator()

    if args.batch:
        print("Batch generation coming soon!")
    else:
        generator.run_interactive()

if __name__ == "__main__":
    main()
