import os
import re
from pathlib import Path

# Final comprehensive concept mappings
CONCEPT_MAP = {
    "接續相生": "theory/11_五行相生章|接續相生",
    "克處逢生": "theory/13_克處逢生章|克處逢生",
    "六神": "theory/18_六神章|六神",
    "月將": "theory/16_月建章|月將",
    "月將章": "theory/16_月建章",
    "theory/16_月將章": "theory/16_月建章",
    "隨鬼入墓": "theory/30_隨鬼入墓章|隨鬼入墓",
    "隨鬼入墓章": "theory/30_隨鬼入墓章",
    "出空": "glossary/旬空|出空",
    "旬空": "glossary/旬空",
    "月破": "glossary/月破",
    "日辰": "glossary/日辰",
    "日建": "glossary/日辰|日建",
    "太歲": "glossary/日辰|太歲",
    "用神": "glossary/用神",
    "元神": "glossary/元神",
    "原神": "glossary/元神|原神",
    "忌神": "glossary/忌神",
    "原神章": "theory/09_元神忌神仇神章",
    "忌神章": "theory/10_元神忌神衰旺章",
    "theory/09_原神章": "theory/09_元神忌神仇神章",
    "theory/10_忌神章": "theory/10_元神忌神衰旺章",
    "仇神": "glossary/仇神",
    "世爻": "glossary/世爻",
    "應爻": "glossary/應爻",
    "父母爻": "glossary/父母爻",
    "兄弟爻": "glossary/兄弟爻",
    "子孫爻": "glossary/子孫爻",
    "妻財爻": "glossary/妻財爻",
    "官鬼爻": "glossary/官鬼爻",
    "六沖": "glossary/六沖",
    "六合": "glossary/六合",
    "三合局": "glossary/三合局",
    "動爻": "glossary/動爻",
    "反吟": "glossary/反吟",
    "伏吟": "glossary/伏吟",
    "化進神": "glossary/化進神",
    "化退神": "glossary/化退神",
    "化墓": "glossary/化墓",
    "化絕": "glossary/化絕",
    "化空": "glossary/化空",
    "合住": "glossary/合住",
    "合起": "glossary/合起",
    "合絆": "glossary/合住|合絆",
    "化鬼": "glossary/官鬼爻|化鬼",
    "化扶": "glossary/回頭生|化扶",
    "回頭克": "glossary/回頭克",
    "回頭生": "glossary/回頭生",
    "入墓": "glossary/入墓",
    "沖開": "glossary/合住|沖開",
    "絕卦": "glossary/化絕|絕卦",
    "三合木局": "glossary/三合局|三合木局",
    "三合水局": "glossary/三合局|三合水局",
    "三合金局": "glossary/三合局|三合金局",
    "三合火局": "glossary/三合局|三合火局",
    "六沖變六合": "glossary/六合|六沖變六合",
    "六合變六合": "glossary/六合|六合變六合",
    "動不為空": "glossary/動爻|動不為空",
    "物窮則變": "theory/24_卦變生克墓絕章|物窮則變",
    "器滿則傾": "theory/24_卦變生克墓絕章|器滿則傾",
    "月克": "theory/12_五行相克章|月克",
    "日生": "theory/11_五行相生章|日生",
    "月絕": "glossary/化絕|月絕",
    "日刑": "glossary/三刑|日刑",
    # Point missing high-numbered chapters to learning map
    "theory/32_兩現章": "000_增刪卜易_學習地圖|兩現章",
    "theory/34_黃金策千金賦": "000_增刪卜易_學習地圖|黃金策千金賦",
    "theory/37_終身財福章": "000_增刪卜易_學習地圖|終身財福章",
    "theory/38_終身功名章": "000_增刪卜易_學習地圖|終身功名章",
    "theory/39_壽元章": "000_增刪卜易_學習地圖|壽元章",
    "theory/40_趨避章": "000_增刪卜易_學習地圖|趨避章",
}

def get_all_md_files(base_dir):
    files = {}
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if f.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, f), base_dir).replace('\\', '/')
                basename = os.path.splitext(f)[0]
                files[rel_path] = rel_path
                files[os.path.splitext(rel_path)[0]] = rel_path
                if basename not in files:
                    files[basename] = rel_path
    return files

def fix_links():
    base_dir = Path.cwd()
    all_files = get_all_md_files(base_dir)
    link_regex = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    
    modified_files = 0
    total_fixes = 0

    for md_file in Path(base_dir).rglob('*.md'):
        if md_file.name in ['fix_links.py', 'check_links.py']: continue
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            def replace_link(match):
                nonlocal total_fixes
                target = match.group(1).strip()
                alias = match.group(2)
                
                # Check for direct matches or conceptual mappings
                target_norm = target.replace('\\', '/')
                if target_norm in all_files or target in all_files: return match.group(0)
                
                if target in CONCEPT_MAP:
                    total_fixes += 1
                    mapped = CONCEPT_MAP[target]
                    return f"[[{mapped}|{alias}]]" if alias else f"[[{mapped}]]"
                
                # Fuzzy match case numbers for broken README links
                if target.startswith('case_'):
                    m = re.match(r'case_(\d+)', target)
                    if m:
                        case_num = m.group(1).zfill(3) # Ensure 3 digits for consistency
                        potential_matches = [p for name, p in all_files.items() if name.startswith(f"case_{case_num}") and '/' in p]
                        if potential_matches:
                            total_fixes += 1
                            best_match = potential_matches[0]
                            link_text = os.path.splitext(os.path.basename(best_match))[0]
                            return f"[[{best_match}|{alias if alias else link_text}]]"
                
                return match.group(0)

            new_content = link_regex.sub(replace_link, content)
            if new_content != content:
                md_file.write_text(new_content, encoding='utf-8')
                modified_files += 1
                print(f"Fixed: {md_file.relative_to(base_dir)}")
        except Exception: pass

    print(f"\nFinal Pass Repair Complete:\n - Modified: {modified_files}\n - Fixed: {total_fixes}")

if __name__ == "__main__":
    fix_links()
