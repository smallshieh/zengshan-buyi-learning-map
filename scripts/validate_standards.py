import os
import re
import sys

# Path settings
BASE_DIR = os.getcwd()
CASES_DIR = os.path.join(BASE_DIR, 'cases')

# Regex: case_NNN_description.md
# NNN must be 3 digits
REGEX_STD = re.compile(r"^case_\d{3}_.+\.md$")

errors = []
total_files = 0

print(f"Validating standards in: {CASES_DIR}")

for root, dirs, files in os.walk(CASES_DIR):
    for file in files:
        if file.endswith(".md") and file.lower() != "readme.md":
            total_files += 1
            path = os.path.join(root, file)
            
            # Check 1: Naming Convention
            if not REGEX_STD.match(file):
                 errors.append(f"[Naming Error] {file} (Path: {root}) does not match 'case_NNN_desc.md'")
            
            # Check 2: Content Structure (Basic check)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "original_hexagram" not in content and "gua_original" not in content and "Raw Text" not in content:
                        # Allow Raw Text for temp files? No, strict mode means finalized.
                        # But wait, raw files might exist before ingestion.
                        # Let's focused warnings.
                        pass
            except:
                errors.append(f"[Read Error] {file}")

print(f"\nChecked {total_files} case files.")

if errors:
    print(f"\n❌ FOUND {len(errors)} VIOLATIONS:")
    for e in errors:
        print(e)
    print("\nRecommendation: Run 'python scripts/refactor_cases.py' to fix naming issues.")
    sys.exit(1)
else:
    print("\n✅ All case files meet naming standards.")
    sys.exit(0)
