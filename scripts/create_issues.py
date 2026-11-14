"""Create labels and all issues with the GitHub CLI.
  gh auth login
  python scripts/create_issues.py            # run ONCE
Fill ASSIGNEES with GitHub usernames to assign by role (leave "" to assign later in the web UI).
"""
import subprocess
from issues_data import ISSUES, LABELS

ASSIGNEES = {"role-1-mgmt": "", "role-2-data": "", "role-3-frontend": "", "role-4-deploy": ""}


def gh(*args):
    subprocess.run(["gh", *args], check=True)


if __name__ == "__main__":
    for name, color in LABELS.items():
        gh("label", "create", name, "--color", color, "--force")
    for i in ISSUES:
        cmd = ["issue", "create", "--title", i["title"], "--body", i["body"], "--label", ",".join(i["labels"])]
        who = ASSIGNEES.get(i["labels"][0], "")
        if who:
            cmd += ["--assignee", who]
        gh(*cmd)
    print(f"Created {len(ISSUES)} issues")
