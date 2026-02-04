import os
import sys

# Set specific encoding for output to handle Chinese characters in console
sys.stdout.reconfigure(encoding='utf-8')

reference_dir = os.path.join(os.getcwd(), 'reference')

print(f"Scanning directory: {reference_dir}")

target_file = None
try:
    files = os.listdir(reference_dir)
    print(f"Files found: {files}")
    for f in files:
        if "增" in f and f.endswith(".txt"):
            target_file = os.path.join(reference_dir, f)
            print(f"Selected file: {f}")
            break
except Exception as e:
    print(f"Error listing directory: {e}")
    exit(1)

if not target_file:
    print("No matching file found.")
    exit(1)

print(f"Attempting to read: {target_file}")

content = ""
try:
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print("Success reading with utf-8")
except UnicodeDecodeError:
    print("Failed utf-8, trying gb18030...")
    try:
        with open(target_file, 'r', encoding='gb18030') as f:
            content = f.read()
        print("Success reading with gb18030")
    except Exception as e:
        print(f"Failed gb18030: {e}")
        exit(1)

print(f"Content length: {len(content)}")

# Test search with Synonyms as user suggested
keywords = ["占痘", "痘疹", "占病", "開店", "開張", "借貸", "求財"]
print("\n--- Testing Search (Synonym Check) ---")
for kw in keywords:
    count = content.count(kw)
    print(f"Keyword '{kw}': found {count} times")
