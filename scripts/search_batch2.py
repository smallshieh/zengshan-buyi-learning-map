import os

base_dir = "."
ref_dir = os.path.join(base_dir, "reference")
target_file = None

if os.path.exists(ref_dir):
    for f in os.listdir(ref_dir):
        if "增" in f and f.endswith(".txt") and os.path.getsize(os.path.join(ref_dir, f)) > 100000:
            target_file = os.path.join(ref_dir, f)
            break

if not target_file:
    print("Target file not found")
    exit()

keywords = [
    "占痘", 
    "占病源", 
    "占延醫", 
    "占開店", 
    "占借貸", 
    "占買賣六畜"
]

try:
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
except:
    try:
        with open(target_file, 'r', encoding='gb18030') as f:
            content = f.read()
    except:
        exit()

output_path = os.path.join("scripts", "search_results_batch2.txt")
with open(output_path, "w", encoding="utf-8") as out:
    for kw in keywords:
        out.write(f"\n--- Searching for: {kw} ---\n")
        start = 0
        count = 0
        while True:
            idx = content.find(kw, start)
            if idx == -1:
                break
            
            ctx_start = max(0, idx - 100)
            ctx_end = min(len(content), idx + 800) 
            
            out.write(f"Match {count+1} at {idx}:\n")
            out.write(content[ctx_start:ctx_end].replace('\n', ' ') + "\n\n")
            
            start = idx + 1
            count += 1
            if count >= 2: 
                break
        if count == 0:
            out.write("Not found.\n")

print(f"Done. Written to {output_path}")
