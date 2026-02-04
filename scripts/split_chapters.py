import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Source/Target Paths
source_file = os.path.join(os.getcwd(), 'legacy_docs', '增刪卜易.txt')
output_dir = os.path.join(os.getcwd(), 'reference', 'chapters')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

def main():
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(source_file, 'r', encoding='gb18030') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read source file: {e}")
            return

    print(f"Loaded source: {len(content)} chars")

    # Regex to find chapter headers
    # Pattern explanation:
    # Matches lines like "第十八章 占..." or "卷一" or just keywords if structure is loose
    # Based on observation, chapters might look like: "卷之一", "章第XX", etc.
    # Let's try a generic pattern for "Chapter" or "Section"
    
    # We will split by a specific delimiter if possible, or use a robust regex loop
    # Assuming "卷之" or "章" as major delimiters.
    
    # Let's simple split by lines and try to detect headers
    lines = content.split('\n')
    
    current_chapter_title = "preface"
    current_chapter_lines = []
    chapter_count = 0
    
    # Regex for Chapter Titles
    # Example: "第一章", "第x章", "卷之x"
    # Or titles like "黃金策總斷千金賦" which are distinct
    
    # For Zeng Shan Bu Yi, structure is roughly:
    # 卷之一
    # Chapter Title
    # Text...
    
    # Let's rely on valid large headers? No, text is flat.
    # Let's try matching specific pattern "章第" or similar if standard.
    # If standard is weak, we might stick to splitting by "卷" (Volume) first as they are larger chunks.
    
    # Trying generic "Volume" split first
    re_volume = re.compile(r"^\s*卷之[一二三四五六七八九十]+\s*$", re.MULTILINE)
    
    # Trying "Chapter" split? '第.*章'
    re_chapter = re.compile(r"^\s*第[一二三四五六七八九十百]+章\s+.*$")
    
    for line in lines:
        stripped = line.strip()
        
        # Check if line is a chapter header
        # Using a loose heuristic: start with "第" end with "章" and length < 20
        # OR specific known titles list?
        
        is_header = False
        if re_chapter.match(stripped):
            is_header = True
        elif len(stripped) < 30 and ("章第" in stripped or (stripped.startswith("第") and "章" in stripped)):
             is_header = True
        
        if is_header:
            # Save previous chapter
            if current_chapter_lines:
                save_chapter(current_chapter_title, current_chapter_lines, output_dir, chapter_count)
                chapter_count += 1
            
            # Start new
            current_chapter_title = stripped.replace(" ", "_").replace("/", "-")
            current_chapter_lines = [line]
        else:
            current_chapter_lines.append(line)
            
    # Save last
    if current_chapter_lines:
        save_chapter(current_chapter_title, current_chapter_lines, output_dir, chapter_count)

    print(f"Split complete. Total files: {chapter_count + 1}")

def save_chapter(title, lines, out_dir, count):
    # Clean filename
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
    filename = f"chap_{count:03d}_{clean_title}.txt"
    path = os.path.join(out_dir, filename)
    
    text = "\n".join(lines)
    
    # Skip too small files (noise)
    if len(text) < 50:
        return

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Saved: {filename} ({len(text)} chars)")

if __name__ == "__main__":
    main()
