import os
import re
import shutil

# Base directory
BASE_DIR = r"c:\Users\smallshieh\Obsidian筆記\cases"

# Regex for metadata
RE_DATE = re.compile(r"^date_lunar:\s*(.*)$", re.MULTILINE)
RE_QUESTION = re.compile(r"^question:\s*(.*)$", re.MULTILINE)
RE_TAGS = re.compile(r"^tags:\s*(.*)$", re.MULTILINE)

def get_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        date_match = RE_DATE.search(content)
        question_match = RE_QUESTION.search(content)
        return {
            "date": date_match.group(1).strip() if date_match else "Unknown",
            "question": question_match.group(1).strip() if question_match else "Unknown",
            "path": filepath,
            "filename": os.path.basename(filepath),
            "content": content
        }
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    all_cases = []
    
    # 1. Scan files
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md") and file.startswith("case_"):
                path = os.path.join(root, file)
                meta = get_metadata(path)
                if meta:
                    meta['category'] = os.path.basename(root)
                    all_cases.append(meta)

    # 2. Deduplicate
    unique_cases = {}
    duplicates_to_remove = []

    for case in all_cases:
        key = (case['date'], case['question'])
        if key in unique_cases:
            # Conflict! Decide which to keep.
            # Prefer ones NOT in "Other" or "Misc" if possible?
            # Prefer the one with standard naming?
            # For now, keep the first one found, or check content length/quality?
            # Let's keep the one that "Standardization" touched (Mermaid presence).
            existing = unique_cases[key]
            
            # Simple heuristic: keep the one with larger size (likely more content/diagrams)
            if len(case['content']) > len(existing['content']):
                duplicates_to_remove.append(existing['path'])
                unique_cases[key] = case
            else:
                duplicates_to_remove.append(case['path'])
        else:
            unique_cases[key] = case

    # Remove duplicates
    print(f"Removing {len(duplicates_to_remove)} duplicates...")
    for p in duplicates_to_remove:
        try:
            os.remove(p)
            print(f"Deleted: {p}")
        except OSError as e:
            print(f"Error deleting {p}: {e}")

    # 3. Sort & Renumber
    # Sort by Category, then by Date (if possible) or Filename
    # To sort by Category ensure specific order:
    CAT_ORDER = ["六親", "官訟", "功名", "求財", "疾病", "出行", "行人", "趨避", "風水", "其他"]
    
    final_list = list(unique_cases.values())
    
    def sort_key(c):
        cat_index = CAT_ORDER.index(c['category']) if c['category'] in CAT_ORDER else 99
        return (cat_index, c['filename'])

    final_list.sort(key=sort_key)

    # 4. Rename
    print("Renumbering...")
    for i, case in enumerate(final_list, 1):
        new_id = f"case_{i:03d}"
        old_path = case['path']
        folder = os.path.dirname(old_path)
        
        # Keep original descriptive suffix if possible?
        # filename is like `case_XXX_description.md`
        # We want `case_NNN_description.md`
        # Extract description
        match = re.match(r"case_\d+_(.*)\.md", case['filename'])
        desc = match.group(1) if match else "unknown"
        
        new_filename = f"{new_id}_{desc}.md"
        new_path = os.path.join(folder, new_filename)
        
        if old_path != new_path:
            # Check collision with existing file in new path (if we are shuffling)
            if os.path.exists(new_path) and new_path not in [x['path'] for x in final_list]:
                 # Standard collision
                 pass
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {os.path.basename(old_path)} -> {new_filename}")
                # Update content ID if needed? (Not doing content update for ID inside text, assuming text uses generic references)
            except OSError as e:
                print(f"Error renaming {old_path}: {e}")

if __name__ == "__main__":
    main()
