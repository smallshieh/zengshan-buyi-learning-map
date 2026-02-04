import json
import os
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "guali_db.json"
CASES_DIR = BASE_DIR / "cases"

def load_db():
    if not DB_FILE.exists():
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def update_md_with_yaml(case_data):
    rel_path = case_data.get("_source_file")
    if not rel_path:
        return
    
    full_path = BASE_DIR / rel_path
    if not full_path.exists():
        # Try to find it if it was moved/renamed by refactor script
        # The JSON _source_file usually reflects the path at time of extraction.
        # But if the file was just renamed in same folder, we might need a search.
        fname = os.path.basename(rel_path)
        potential_files = list(CASES_DIR.rglob(fname))
        if not potential_files:
            print(f"File not found: {rel_path}")
            return
        full_path = potential_files[0]

    # Prepare YAML
    # We want to be detailed for Dataview
    yaml_fields = {
        "date_lunar": case_data.get("time", ""),
        "question": case_data.get("subject", ""),
        "original_hexagram": case_data.get("original_hexagram", ""),
        "changed_hexagram": case_data.get("changed_hexagram", ""),
        "result": case_data.get("outcome", ""),
        "tags": ["增刪卜易/卦例"]
    }
    
    # Extract "Category" from filename or path
    category_match = re.search(r'case_\d+_(.*?)_', full_path.name)
    if category_match:
        cat = category_match.group(1)
        yaml_fields["tags"].append(f"增刪卜易/卦例/{cat}")
    
    # Specific logic for Weather Analysis: Identify the 'Self' line (世爻)
    # The original_hexagram often looks like: "大壯卦；世在三爻父母午火"
    orig_hex = case_data.get("original_hexagram", "")
    if orig_hex and "世" in orig_hex:
        # Try to extract the relation (父母, 兄弟, etc.)
        relation_match = re.search(r'世[^：:]*[：:]\s*([^\s；;，,]+)', orig_hex)
        if relation_match:
            # Clean up relation (e.g. 父母午火 -> 父母)
            rel = relation_match.group(1)
            for r in ["父母", "兄弟", "妻財", "官鬼", "子孫"]:
                if r in rel:
                    yaml_fields["self_relation"] = r
                    break

    # Read existing content (remove old YAML if exists)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove existing frontmatter if any
    content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
    
    # Construct new frontmatter
    yaml_lines = ["---"]
    for k, v in yaml_fields.items():
        if isinstance(v, list):
            yaml_lines.append(f"{k}: [{', '.join(v)}]")
        else:
            # Escape quotes in string
            if v:
                v_clean = str(v).replace('"', '\\"')
                yaml_lines.append(f'{k}: "{v_clean}"')
            else:
                yaml_lines.append(f'{k}: ""')
    yaml_lines.append("---")
    
    new_content = "\n".join(yaml_lines) + "\n" + content.lstrip()
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated: {full_path.name}")

def main():
    db = load_db()
    print(f"Processing {len(db)} entries...")
    for entry in db:
        update_md_with_yaml(entry)

if __name__ == "__main__":
    main()
