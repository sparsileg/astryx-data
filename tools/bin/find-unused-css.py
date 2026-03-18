#!/usr/bin/env python3
"""
find-unused-css.py
Finds CSS selectors not referenced in any source file.

Usage:
    python find-unused-css.py --css <file> [--css <file> ...] \
                               [--dir <folder> ...] \
                               [--file <file> ...]

Options:
    --css   CSS file to analyze (can be specified multiple times)
    --dir   Directory to search recursively (can be specified multiple times)
    --file  Single source file to include (can be specified multiple times)

Example:
    python find-unused-css.py --css css/base.css --css css/forms.css \
                               --dir js/ --dir src/ --file index.html
"""

import argparse
import os
import re
import sys


# File extensions to search in source files
SOURCE_EXTENSIONS = {'.js', '.html', '.ts', '.jsx', '.tsx', '.py'}


def collect_source_files(dirs, files):
    """Collect all source files from specified directories and individual files."""
    source_files = set()

    for d in dirs:
        if not os.path.isdir(d):
            print(f"Warning: directory '{d}' not found, skipping.", file=sys.stderr)
            continue
        for root, _, filenames in os.walk(d):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in SOURCE_EXTENSIONS:
                    source_files.add(os.path.join(root, fname))

    for f in files:
        if not os.path.isfile(f):
            print(f"Warning: file '{f}' not found, skipping.", file=sys.stderr)
            continue
        source_files.add(f)

    return source_files


def read_source_content(source_files):
    """Read and concatenate all source file contents into one big string."""
    parts = []
    for path in source_files:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                parts.append(f.read())
        except Exception as e:
            print(f"Warning: could not read '{path}': {e}", file=sys.stderr)
    return '\n'.join(parts)


def extract_selectors(css_file):
    """
    Extract class and ID selectors from a CSS file.
    Returns a list of (selector_string, base_name) tuples.
    """
    try:
        with open(css_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading CSS file '{css_file}': {e}", file=sys.stderr)
        return []

    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # Remove @keyframes blocks entirely (contain % selectors we don't care about)
    content = re.sub(r'@keyframes\s+\S+\s*\{[^}]*\}', '', content, flags=re.DOTALL)

    selectors = []
    seen = set()

    # Find all selector blocks: everything before a {
    # Split on } to get individual rule blocks, then grab the selector part
    rule_pattern = re.compile(r'([^{}]+)\{', re.MULTILINE)

    for match in rule_pattern.finditer(content):
        selector_block = match.group(1).strip()

        # Skip @rules (media, supports, etc.)
        if selector_block.startswith('@'):
            continue

        # Split comma-separated selectors
        for raw_selector in selector_block.split(','):
            selector = raw_selector.strip()
            if not selector:
                continue

            # Extract all class and ID names from this selector
            names = re.findall(r'[.#]([a-zA-Z][a-zA-Z0-9_-]*)', selector)
            for name in names:
                if name not in seen:
                    seen.add(name)
                    selectors.append((selector.strip(), name))

    return selectors


def get_fragments(name):
    """
    Split a hyphenated class name into meaningful fragments.
    For 'status-planning', returns ['status', 'planning'].
    Ignores single-character fragments.
    """
    parts = re.split(r'[-_]', name)
    return [p for p in parts if len(p) > 1]


def check_selectors(css_file, source_content):
    """
    Check selectors in css_file against source_content.
    Returns three lists of (selector, name) tuples:
      - unused:   full name not found, no fragments found either
      - dynamic:  full name not found, but fragments suggest dynamic construction
      - used:     full name found (not returned, just counted)
    """
    selectors = extract_selectors(css_file)
    unused = []
    dynamic = []
    used_count = 0

    for selector, name in selectors:
        # First: search for the full name as a whole word
        full_pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(full_pattern, source_content):
            used_count += 1
            continue

        # Full name not found — check fragments for dynamic construction
        fragments = get_fragments(name)
        if len(fragments) >= 2:
            # Check if at least the prefix fragment appears in source
            # (e.g. 'status' from 'status-planning')
            prefix = fragments[0]
            prefix_pattern = r'\b' + re.escape(prefix) + r'\b'
            if re.search(prefix_pattern, source_content):
                dynamic.append((selector, name, prefix))
                continue

        unused.append((selector, name))

    return unused, dynamic, used_count


def main():
    parser = argparse.ArgumentParser(
        description='Find CSS selectors not referenced in source files.'
    )
    parser.add_argument(
        '--css', action='append', metavar='FILE', default=[],
        help='CSS file to analyze (can be specified multiple times)'
    )
    parser.add_argument(
        '--dir', action='append', metavar='DIR', default=[],
        help='Directory to search recursively (can be specified multiple times)'
    )
    parser.add_argument(
        '--file', action='append', metavar='FILE', default=[],
        help='Single source file to include (can be specified multiple times)'
    )

    args = parser.parse_args()

    if not args.css:
        print("Error: at least one --css file is required.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if not args.dir and not args.file:
        print("Error: at least one --dir or --file is required.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Validate CSS files
    for css_file in args.css:
        if not os.path.isfile(css_file):
            print(f"Error: CSS file '{css_file}' not found.", file=sys.stderr)
            sys.exit(1)

    # Collect and read all source files
    print(f"Collecting source files...")
    source_files = collect_source_files(args.dir, args.file)
    print(f"Found {len(source_files)} source file(s) to search.")
    print()

    source_content = read_source_content(source_files)

    # Check each CSS file
    total_unused = 0
    total_dynamic = 0
    for css_file in args.css:
        unused, dynamic, used_count = check_selectors(css_file, source_content)
        total_unused += len(unused)
        total_dynamic += len(dynamic)

        print(f"{'='*60}")
        print(f"CSS File: {css_file}")
        print(f"{'='*60}")
        print(f"  Used: {used_count}  |  Possibly dynamic: {len(dynamic)}  |  Unused: {len(unused)}")
        print()

        if unused:
            print(f"  UNUSED ({len(unused)}) — not found anywhere in source:")
            for selector, name in unused:
                print(f"    [{name}]  {selector}")
            print()

        if dynamic:
            print(f"  POSSIBLY DYNAMIC ({len(dynamic)}) — full name absent but prefix found in source:")
            for selector, name, prefix in dynamic:
                print(f"    [{name}]  {selector}  (prefix '{prefix}' found)")
            print()

        if not unused and not dynamic:
            print("  ✓ No unused selectors found.")
            print()

    print(f"{'='*60}")
    print(f"Total unused:          {total_unused}")
    print(f"Total possibly dynamic: {total_dynamic}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
