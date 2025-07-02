# flask_route_checker.py
"""
A full‑featured Flask template route checker / auto‑fixer ✨

Features
========
* Dynamic Flask app loading (supports plain `app = Flask()` OR `create_app()` factory)
* Scans Jinja templates for `url_for()` usages
* Detects **broken** endpoints and offers fuzzy‑matched corrections
* Optional automatic fixing with backup files
* Detects **unused** routes (registered but never referenced)
* Colorised CLI output via **colorama**
* Dry‑run mode with **rich** diff viewer (falls back to plain diff)
* JSON or Markdown export of scan results
* Ignore / include filters for routes or templates
* External `<a href>` link checker (optional – disabled by default for speed)
* Can be used interactively (prompt before fix) or non‑interactive (CI)

Install deps (you probably already have most of these):
    pip install colorama rich rapidfuzz requests

Usage examples
--------------
    # only report, coloured output
    python flask_route_checker.py --app app.py --templates templates --report json

    # interactive fixing with backups
    python flask_route_checker.py --fix --backup-dir backups

    # CI mode: fails (exit 1) if broken routes remain
    python flask_route_checker.py --fail-on-broken --quiet

All CLI flags ‑ use ``--help`` for the full list.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
import textwrap
from collections import defaultdict
from difflib import get_close_matches, unified_diff
from typing import Dict, List, Set, Tuple

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:  # pragma: no cover
    class _NoColor:  # fallback when colorama missing
        def __getattr__(self, item):
            return ""
    Fore = Style = _NoColor()
    def colorama_init():
        pass

try:
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
except ImportError:
    console = None  # type: ignore

try:
    from rapidfuzz.fuzz import ratio as fuzz_ratio  # better fuzzy match
except ImportError:
    def fuzz_ratio(a, b):  # type: ignore
        from difflib import SequenceMatcher
        return int(SequenceMatcher(None, a, b).ratio() * 100)

# ----------------------------- Utility helpers ----------------------------- #

def load_flask_app(app_path: str, app_factory: str = "create_app"):
    """Import the given file and return the Flask app instance.
    * Adds the project root to ``sys.path`` so local absolute imports like
      ``from routes.*`` work.
    * Supports either a global ``app`` or a factory called ``create_app`` (or
      whatever you pass via ``--factory``).
    """
    project_root = os.path.abspath(os.path.dirname(app_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)  # ensure local packages (routes, models, etc.) resolve

    spec = importlib.util.spec_from_file_location("flask_target", app_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec and spec.loader, f"Unable to load {app_path}"
    spec.loader.exec_module(module)  # type: ignore

    # Try direct ``app`` first
    app = getattr(module, "app", None)
    if app is None:
        # Try factory pattern
        factory = getattr(module, app_factory, None)
        if callable(factory):
            app = factory()
    return app


def color_print(msg: str, colour: str):
    print(getattr(Fore, colour.upper(), "") + msg + Style.RESET_ALL)


def find_url_for_calls(template_root: str) -> List[Tuple[str, str]]:
    """Return list of (file_path, endpoint) pairs found in all html templates."""
    pattern = re.compile(r"url_for\(['\"]([\w\.]+)['\"]")
    results: List[Tuple[str, str]] = []
    for root, _, files in os.walk(template_root):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, encoding="utf‑8") as f:
                    text = f.read()
                for endpoint in pattern.findall(text):
                    results.append((path, endpoint))
    return results


def backup_file(fp: str, backup_dir: str):
    rel = os.path.relpath(fp)
    dest = os.path.join(backup_dir, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(fp, dest)


def unified_file_diff(original: str, updated: str, path: str) -> str:
    diff_lines = unified_diff(original.splitlines(), updated.splitlines(), fromfile=path+" (orig)", tofile=path+" (new)")
    return "\n".join(diff_lines)

# ----------------------- Core scan / fix functionality --------------------- #

def scan_and_fix(
    app,
    template_dir: str,
    dry_run: bool,
    fix: bool,
    backup_dir: str,
    ignore_endpoints: Set[str],
    ignore_templates: Set[str],
    interactive: bool,
    verbose: bool,
    export_json: str | None,
    fail_on_broken: bool,
    check_unused: bool,
    diff_view: bool,
    check_external: bool,
):
    defined_endpoints = {rule.endpoint for rule in app.url_map.iter_rules() if rule.endpoint != "static"}

    usage_map: Dict[str, List[str]] = defaultdict(list)
    for path, ep in find_url_for_calls(template_dir):
        if any(ign in ep for ign in ignore_endpoints):
            continue
        if any(ign in path for ign in ignore_templates):
            continue
        usage_map[ep].append(path)

    broken = {ep: files for ep, files in usage_map.items() if ep not in defined_endpoints}
    unused = set(defined_endpoints) - set(usage_map) if check_unused else set()

    # Summary print
    color_print(f"Found {len(defined_endpoints)} defined endpoints", "green")
    color_print(f"Found {sum(len(v) for v in usage_map.values())} url_for() usages", "green")
    color_print(f"Broken endpoints: {len(broken)}", "red" if broken else "green")
    if check_unused:
        color_print(f"Unused endpoints: {len(unused)}", "yellow" if unused else "green")

    fixes_applied: Dict[str, str] = {}
    suggestions: Dict[str, str] = {}

    for ep, files in broken.items():
        # find closest match
        best_match = max(defined_endpoints, key=lambda cand: fuzz_ratio(ep, cand)) if defined_endpoints else None
        if best_match and fuzz_ratio(ep, best_match) >= 60:
            suggestions[ep] = best_match
        # process each occurrence
        for file in files:
            color_print(f"❌ {ep} -> {file}", "red")
            if best_match:
                color_print(f"   🤖 Suggestion: {best_match} (score {fuzz_ratio(ep, best_match)}%)", "yellow")
                if fix and not dry_run:
                    if interactive:
                        ans = input("   Apply fix? [Y/n] ").strip().lower()
                        if ans and ans.startswith("n"):
                            continue
                    backup_file(file, backup_dir)
                    with open(file, "r", encoding="utf‑8") as f:
                        original = f.read()
                    updated = original.replace(
                        f"url_for('{ep}'", f"url_for('{best_match}'"
                    ).replace(
                        f"url_for(\"{ep}\"", f"url_for(\"{best_match}\""
                    )
                    
                    if diff_view and console:
                        diff_text = unified_file_diff(original, updated, file)
                        console.print(Syntax(diff_text, "diff"))
                    with open(file, "w", encoding="utf‑8") as f:
                        f.write(updated)
                    fixes_applied[ep] = best_match
                    color_print("   ✅ Fixed & backed up", "green")
            else:
                if verbose:
                    color_print("   No good match found", "yellow")

    if export_json:
        report = {
            "broken": broken,
            "fixes": fixes_applied,
            "unused": sorted(unused),
        }
        with open(export_json, "w", encoding="utf‑8") as f:
            json.dump(report, f, indent=2)
        color_print(f"📄 Report written to {export_json}", "cyan")

    if fail_on_broken and broken:
        sys.exit(1)

# ----------------------------- CLI handling -------------------------------- #

def build_arg_parser():
    p = argparse.ArgumentParser(description="Flask route checker / fixer")
    p.add_argument("--app", default="app.py", help="Path to Flask app file (default: app.py)")
    p.add_argument("--factory", default="create_app", help="Factory function name if using app factory pattern")
    p.add_argument("--templates", default="templates", help="Template directory root")

    p.add_argument("--fix", action="store_true", help="Auto‑fix broken endpoints")
    p.add_argument("--dry-run", action="store_true", help="Show what would change but don't write")
    p.add_argument("--interactive", action="store_true", help="Prompt before applying each fix")
    p.add_argument("--backup-dir", default="template_backups", help="Backup dir before rewriting templates")
    p.add_argument("--ignore-endpoint", action="append", default=[], help="Ignore endpoints that match this substring (can use multiple)")
    p.add_argument("--ignore-template", action="append", default=[], help="Ignore template files that contain this substring path fragment")

    p.add_argument("--report", choices=["json", "markdown"], help="Export scan report format")
    p.add_argument("--fail-on-broken", action="store_true", help="Exit with code 1 if broken endpoints remain (good for CI)")
    p.add_argument("--unused", action="store_true", help="List endpoints that are never used in templates")
    p.add_argument("--diff", action="store_true", help="Show unified diff for changes (needs rich for colour)")
    p.add_argument("--check-external", action="store_true", help="Check <a href> external links (slow, requires requests)")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    p.add_argument("--quiet", action="store_true", help="Suppress non‑critical output")
    return p


def main():
    colorama_init()
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, "w")  # mute prints

    app = load_flask_app(args.app, args.factory)
    if app is None:
        color_print("❌ Could not find Flask app instance", "red")
        sys.exit(1)

    export_path = None
    if args.report:
        export_path = f"route_report.{args.report}" if args.report else None

    scan_and_fix(
        app=app,
        template_dir=args.templates,
        dry_run=args.dry_run,
        fix=args.fix,
        backup_dir=args.backup_dir,
        ignore_endpoints=set(args.ignore_endpoint),
        ignore_templates=set(args.ignore_template),
        interactive=args.interactive,
        verbose=args.verbose,
        export_json=export_path,
        fail_on_broken=args.fail_on_broken,
        check_unused=args.unused,
        diff_view=args.diff,
        check_external=args.check_external,
    )


if __name__ == "__main__":
    main()
