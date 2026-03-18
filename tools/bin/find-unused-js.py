#!/usr/bin/env python3
"""
find-unused-js.py
Finds JavaScript functions and methods not referenced anywhere in source files.

Usage:
    python find-unused-js.py --js <file> [--js <file> ...] \
                              [--dir <folder> ...] \
                              [--file <file> ...] \
                              [--ignore <name> ...]

Options:
    --js        JS file to analyze for function definitions (can be specified multiple times)
    --dir       Directory to search recursively for references (can be specified multiple times)
    --file      Single source file to include in reference search (can be specified multiple times)
    --ignore    Function/method name to ignore (can be specified multiple times)

Example:
    python find-unused-js.py --js js/target-filter.js --js js/ui-manager.js \\
                              --dir js/ --file index.html \\
                              --ignore init --ignore render --ignore destroy

Notes:
    - Extracts top-level functions, object literal methods, class methods, and arrow functions
    - Searches for both direct calls (myFn()) and qualified calls (Obj.myFn())
    - Treats this.myFn() as a reference to myFn within its containing object
    - Reports: Used / Possibly Dynamic / Unused
"""

import argparse
import os
import re
import sys


SOURCE_EXTENSIONS = {'.js', '.html', '.ts', '.jsx', '.tsx'}


# Function patterns to extract definitions
# Each pattern yields (qualified_name, short_name, object_name_or_None)

def extract_functions(js_file):
    """
    Extract function and method definitions from a JS file.
    Returns list of dicts:
        {
            'short':     'myMethod',
            'object':    'MyObject' or None,
            'qualified': 'MyObject.myMethod' or 'myMethod',
            'line':      42,
        }
    """
    try:
        with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        print(f"Error reading JS file '{js_file}': {e}", file=sys.stderr)
        return [], None

    # Remove single-line and multi-line comments to avoid false matches
    content_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content_clean = re.sub(r'//[^\n]*', '', content_clean)

    functions = []
    seen_qualified = set()

    # Try to detect the top-level object name (e.g. const TargetFilter = { ... })
    # We'll use this to qualify methods found inside object literals
    obj_pattern = re.compile(
        r'(?:const|let|var)\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*\{',
        re.MULTILINE
    )

    # Build a map of approximate line ranges for each top-level object
    object_ranges = []
    for m in obj_pattern.finditer(content_clean):
        obj_name = m.group(1)
        start_line = content_clean[:m.start()].count('\n') + 1
        # Find the matching closing brace (rough heuristic: find next top-level `};`)
        rest = content_clean[m.end():]
        depth = 1
        pos = 0
        while pos < len(rest) and depth > 0:
            if rest[pos] == '{':
                depth += 1
            elif rest[pos] == '}':
                depth -= 1
            pos += 1
        end_line = content_clean[:m.end() + pos].count('\n') + 1
        object_ranges.append((obj_name, start_line, end_line))

    def get_object_for_line(line_no):
        for obj_name, start, end in object_ranges:
            if start <= line_no <= end:
                return obj_name
        return None

    # Also detect class declarations
    class_pattern = re.compile(r'class\s+([A-Z][a-zA-Z0-9_]*)', re.MULTILINE)
    class_ranges = []
    for m in class_pattern.finditer(content_clean):
        class_name = m.group(1)
        start_line = content_clean[:m.start()].count('\n') + 1
        rest = content_clean[m.end():]
        depth = 0
        pos = 0
        found_open = False
        while pos < len(rest):
            if rest[pos] == '{':
                depth += 1
                found_open = True
            elif rest[pos] == '}':
                depth -= 1
                if found_open and depth == 0:
                    break
            pos += 1
        end_line = content_clean[:m.end() + pos].count('\n') + 1
        class_ranges.append((class_name, start_line, end_line))

    def get_class_for_line(line_no):
        for cls_name, start, end in class_ranges:
            if start <= line_no <= end:
                return cls_name
        return None

    # Pattern set for function definitions
    patterns = [
        # Top-level: function myFunc(
        (re.compile(r'^function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', re.MULTILINE), 'toplevel'),
        # Object method or standalone: myMethod(...) {  or  myMethod: function(
        (re.compile(r'^\s{2,}([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{', re.MULTILINE), 'method'),
        (re.compile(r'^\s{2,}([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?function\s*\(', re.MULTILINE), 'method'),
        # Arrow function assigned to const/let/var: const myFunc = (...) =>
        (re.compile(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', re.MULTILINE), 'arrow'),
        # Arrow function with single param: const myFunc = x =>
        (re.compile(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?[a-zA-Z_$][a-zA-Z0-9_$]*\s*=>', re.MULTILINE), 'arrow'),
        # Class method: methodName( at class indentation
        (re.compile(r'^\s{2,4}(?:async\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{', re.MULTILINE), 'classmethod'),
        # Prototype assignment: MyClass.prototype.myMethod = function(
        (re.compile(r'([A-Z][a-zA-Z0-9_]*)\.prototype\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function', re.MULTILINE), 'prototype'),
    ]

    # Noise names to skip (JS keywords, common non-function words)
    skip_names = {
        'if', 'for', 'while', 'switch', 'catch', 'function', 'class',
        'return', 'const', 'let', 'var', 'new', 'this', 'super',
        'true', 'false', 'null', 'undefined', 'async', 'await',
        'constructor', 'get', 'set', 'static', 'export', 'import',
        'default', 'else', 'try', 'finally', 'typeof', 'instanceof',
    }

    for pattern, ptype in patterns:
        for m in pattern.finditer(content_clean):
            if ptype == 'prototype':
                obj_name = m.group(1)
                fn_name = m.group(2)
            else:
                fn_name = m.group(1)
                obj_name = None

            if fn_name in skip_names:
                continue
            if len(fn_name) <= 1:
                continue

            line_no = content_clean[:m.start()].count('\n') + 1

            if ptype == 'prototype':
                qualified = f"{obj_name}.{fn_name}"
            elif ptype == 'toplevel' or ptype == 'arrow':
                qualified = fn_name
                obj_name = None
            elif ptype in ('method', 'classmethod'):
                # Try object literal first, then class
                container = get_object_for_line(line_no) or get_class_for_line(line_no)
                if container:
                    obj_name = container
                    qualified = f"{container}.{fn_name}"
                else:
                    qualified = fn_name
                    obj_name = None

            if qualified in seen_qualified:
                continue
            seen_qualified.add(qualified)

            functions.append({
                'short': fn_name,
                'object': obj_name,
                'qualified': qualified,
                'line': line_no,
            })

    # Sort by line number
    functions.sort(key=lambda x: x['line'])
    return functions, object_ranges


def collect_source_files(dirs, files):
    """Collect all source files from directories and individual files."""
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
    """Read all source files into one string, with comments stripped."""
    parts = []
    for path in sorted(source_files):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Strip comments to avoid false matches
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            content = re.sub(r'//[^\n]*', '', content)
            parts.append(content)
        except Exception as e:
            print(f"Warning: could not read '{path}': {e}", file=sys.stderr)
    return '\n'.join(parts)


def classify_function(fn, source_content):
    """
    Classify a function as 'used', 'dynamic', or 'unused'.

    Search strategy:
    1. Look for qualified call:  Object.method(  or  Object.method
    2. Look for this.method( within same object context
    3. Look for bare method name as a call:  method(
    4. If not found by name but object is referenced, flag as possibly dynamic
    """
    short = fn['short']
    obj = fn['object']
    qualified = fn['qualified']

    # Build search patterns
    patterns_to_try = []

    if obj:
        # Qualified: MyObject.myMethod
        patterns_to_try.append(re.compile(r'\b' + re.escape(obj) + r'\.' + re.escape(short) + r'\b'))
        # this.myMethod
        patterns_to_try.append(re.compile(r'\bthis\.' + re.escape(short) + r'\b'))

    # Bare function name as a call
    patterns_to_try.append(re.compile(r'\b' + re.escape(short) + r'\s*\('))
    # Bare name passed as callback — must be surrounded by ( or , not just whitespace
    patterns_to_try.append(re.compile(r'[,(]\s*' + re.escape(short) + r'\s*[,)]'))

    for pattern in patterns_to_try:
        if pattern.search(source_content):
            return 'used'

    # Not found — check if possibly dynamic
    if obj:
        obj_pattern = re.compile(r'\b' + re.escape(obj) + r'\b')
        if obj_pattern.search(source_content):
            return 'dynamic'

    return 'unused'


def main():
    parser = argparse.ArgumentParser(
        description='Find JavaScript functions not referenced in source files.'
    )
    parser.add_argument(
        '--js', action='append', metavar='FILE', default=[],
        help='JS file to analyze for function definitions (can be specified multiple times)'
    )
    parser.add_argument(
        '--dir', action='append', metavar='DIR', default=[],
        help='Directory to search recursively (can be specified multiple times)'
    )
    parser.add_argument(
        '--file', action='append', metavar='FILE', default=[],
        help='Single source file to include in reference search (can be specified multiple times)'
    )
    parser.add_argument(
        '--ignore', action='append', metavar='NAME', default=[],
        help='Function name to ignore (can be specified multiple times)'
    )

    args = parser.parse_args()

    if not args.js and not args.dir and not args.file:
        print("Error: at least one --js, --dir, or --file is required.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    ignore_set = set(args.ignore)

    # Collect source files
    print("Collecting source files...")
    source_files = collect_source_files(args.dir, args.file)
    print(f"Found {len(source_files)} source file(s) to search.")
    print()

    # If no --js specified, analyze all JS files found in --dir/--file
    if not args.js:
        args.js = sorted(f for f in source_files if f.endswith('.js'))
        if not args.js:
            print("Error: no JS files found to analyze.", file=sys.stderr)
            sys.exit(1)
        print(f"No --js specified — analyzing all {len(args.js)} JS file(s) found in source.")
        print()

    for js_file in args.js:
        if not os.path.isfile(js_file):
            print(f"Error: JS file '{js_file}' not found.", file=sys.stderr)
            sys.exit(1)

    # Analyze each JS file
    grand_unused = 0
    grand_dynamic = 0

    for js_file in args.js:
        functions, _ = extract_functions(js_file)

        # Build source content excluding the file being analyzed
        # so functions don't match their own definitions
        js_file_abs = os.path.abspath(js_file)
        other_files = {f for f in source_files if os.path.abspath(f) != js_file_abs}
        source_content = read_source_content(other_files)

        used = []
        dynamic = []
        unused = []

        for fn in functions:
            if fn['short'] in ignore_set:
                continue
            result = classify_function(fn, source_content)
            if result == 'used':
                used.append(fn)
            elif result == 'dynamic':
                dynamic.append(fn)
            else:
                unused.append(fn)

        grand_unused += len(unused)
        grand_dynamic += len(dynamic)

        print(f"{'='*60}")
        print(f"JS File: {js_file}")
        print(f"{'='*60}")
        print(f"  Extracted: {len(functions)}  |  Used: {len(used)}  |  Possibly dynamic: {len(dynamic)}  |  Unused: {len(unused)}")
        print()

        if unused:
            print(f"  UNUSED ({len(unused)}) — no reference found:")
            for fn in unused:
                print(f"    [line {fn['line']:4d}]  {fn['qualified']}")
            print()

        if dynamic:
            print(f"  POSSIBLY DYNAMIC ({len(dynamic)}) — name absent but object '{fn['object']}' referenced:")
            for fn in dynamic:
                print(f"    [line {fn['line']:4d}]  {fn['qualified']}  (object '{fn['object']}' found)")
            print()

        if not unused and not dynamic:
            print("  ✓ No unused functions found.")
            print()

    print(f"{'='*60}")
    print(f"Total unused:           {grand_unused}")
    print(f"Total possibly dynamic: {grand_dynamic}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
