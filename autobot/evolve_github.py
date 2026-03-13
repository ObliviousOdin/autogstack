import os
import subprocess
from datetime import datetime
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Read the program
with open("autobot/program.md") as f:
    program = f.read()

# Create new branch name
date = datetime.now().strftime("%Y-%m-%d")
branch = f"auto-{date}-evolution"

print(f"Starting evolution cycle → branch: {branch}")

# Create and switch to new branch
subprocess.run(["git", "checkout", "-B", branch], check=True)

# Ask Claude for ONE focused improvement (as git diff)
prompt = f"""{program}

You are running in GitHub Actions autonomous mode.
Current date: {date}

Perform exactly ONE meaningful improvement to the gstack skills (improve an existing skill or create a new one).

Output ONLY a valid git diff patch (starting with "diff --git").
No explanations, no extra text, no markdown code blocks.
Just the raw diff that can be applied with git apply."""

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=32000,
    temperature=0.7,
    messages=[{"role": "user", "content": prompt}]
)

response = message.content[0].text.strip()

# Save and apply the diff
with open("temp.patch", "w") as f:
    f.write(response)

try:
    subprocess.run(["git", "apply", "temp.patch"], check=True)
    print("✅ Patch applied successfully")
except:
    print("⚠️ No changes or patch failed – skipping commit")
    exit(0)

# Commit and push
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", f"🤖 auto-evolution {date}"], check=True)
subprocess.run(["git", "push", "origin", branch], check=True)

print(f"✅ Successfully pushed new branch: {branch}")
