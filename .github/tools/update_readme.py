import os
import re
from pathlib import Path

tag = os.environ.get("GITHUB_REF_NAME", "").strip()

if not tag:
	raise SystemExit("Missing GITHUB_REF_NAME")

match = re.fullmatch(r"^(?![-_])(?=.{3,}$)(?:[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*)?[vV]?(\d+(?:\.\d+)*)$", tag)

if not match:
	raise SystemExit("Invalid tag format")

version = match.group(1)

readme = Path("README.md")

text = readme.read_text(encoding="utf-8")

new_text, count = re.subn(
	r"(?<!\d)[vV]?\d+(?:\.\d+)+(?!\d)",
	version,
	text,
	count=1
)

if count == 0:
	raise SystemExit("Version line not found in README.md")

if new_text != text:
	readme.write_text(new_text, encoding="utf-8")
	print(f"Updated README to version {version}")
else:
	print("README already up to date")
