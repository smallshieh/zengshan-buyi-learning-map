import os
import re
from pathlib import Path

def get_all_files(base_dir):
    """Recursively get all .md files in the project."""
    files = {}
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if f.endswith('.md'):
                # Store by basename (without .md) for Obsidian link matching
                name = os.path.splitext(f)[0]
                rel_path = os.path.relpath(os.path.join(root, f), base_dir)
                files[name] = rel_path
                # Also store by full relative path for direct links
                files[rel_path.replace('\\', '/')] = rel_path
                # And without extension
                files[os.path.splitext(rel_path.replace('\\', '/'))[0]] = rel_path
    return files

def check_links():
    base_dir = Path.cwd()
    all_files = get_all_files(base_dir)
    
    broken_links = []
    
    # Files to scan
    to_scan = list(Path(base_dir).rglob('*.md'))
    
    # Obsidian link regex: [[link]] or [[link|alias]]
    link_regex = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
    
    for md_file in to_scan:
        rel_src = md_file.relative_to(base_dir)
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            links = link_regex.findall(content)
            
            for target in links:
                target = target.strip()
                # Normalize target (handle subfolders if present in link)
                target_norm = target.replace('\\', '/')
                
                # Check if target exists in our file map
                if target_norm not in all_files and target not in all_files:
                    # Try resolving relative to source if it's a relative path link
                    # But usually Obsidian uses "shortest unique path" or "always full path"
                    # We check if it matches any basename or path we indexed.
                    broken_links.append((str(rel_src), target))
        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    if broken_links:
        print("Broken Links Found:")
        for src, target in broken_links:
            print(f" - In {src}: [[{target}]]")
    else:
        print("No broken links found!")

if __name__ == "__main__":
    check_links()
