"""Write docs/ISSUES.md from issues_data.py (for pasting into GitHub by hand)."""
from pathlib import Path
from issues_data import ISSUES, LABELS

names = {"M": "Role 1: Management and writing", "D": "Role 2: Data", "P": "Role 4: Deployment and integration", "F": "Role 3: Frontend"}
out = ["# Issues", "", "Create all at once with `python scripts/create_issues.py`, or paste each into GitHub. Codes (D3, F7...) are used in dependencies.", ""]
for letter in "MDPF":
    out += [f"## {names[letter]}", ""]
    for i in ISSUES:
        if i["code"].startswith(letter):
            out += [f"### {i['title']}", f"Labels: {', '.join(i['labels'])}", "", i["body"], ""]
Path(__file__).resolve().parents[1].joinpath("docs/ISSUES.md").write_text("\n".join(out))
print("wrote docs/ISSUES.md")
