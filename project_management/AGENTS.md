# Repository Guidelines

This repository is an Obsidian vault of curated notes, examples, and supporting scripts. Keep changes focused on content quality, link integrity, and consistent naming.

## Project Structure & Module Organization

- `cases/`: case studies organized by subfolder; filenames typically start with `case_###_`.
- `theory/`: theory notes and learning path material.
- `glossary/`: term definitions referenced across notes.
- `reference/`: reference material and lookups.
- `legacy_docs/`: older or archived notes.
- `skills/` and `.agent/`: workflow helpers and agent assets.
- `scripts/`: maintenance utilities (see `.agent/instructions.md` for AI-specific logic).

## Build, Test, and Development Commands

Maintenance tasks are in the `scripts/` directory:

- `python scripts/check_links.py` — scans all Markdown files for broken Obsidian links.
- `python scripts/fix_links.py` — applies known link mappings and repairs common link patterns.
- `python scripts/process_book.py` — batches Codex/Ollama extraction into `data/guali_db.json`.

## Coding Style & Naming Conventions

- Markdown: keep frontmatter keys stable and use `[[Obsidian]]` links.
- Filenames: prefer `case_###_description.md` for case notes.
- Indentation: 2 spaces for YAML frontmatter; 4 spaces for Python.
- Scripts: keep functions small, prefer `Path`/`os.path` for portability.

## Testing Guidelines

No automated test suite is present. Validate changes by:

- Running `python check_links.py` after link edits.
- Spot-checking modified notes in Obsidian (links and frontmatter).

## Commit & Pull Request Guidelines

Recent commits use descriptive, imperative messages and occasionally Conventional Commits (e.g., `feat:`). Follow this pattern:

- Use concise, action-oriented subjects.
- Group related fixes per commit.

For pull requests:

- Include a short summary and a bullet list of changes.
- Link related issues or tracking notes if available.
- Provide screenshots when visual layouts or diagrams change.

## Security & Configuration Tips

- Do not rename or move large folders without running link checks.
- Keep scripts in the repo root; avoid hard-coded absolute paths unless required.
