import os
import re
import difflib
from flask import Flask
from importlib.util import spec_from_file_location, module_from_spec

# Load the Flask app dynamically
def load_flask_app(path):
    spec = spec_from_file_location("flask_app", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, 'app', None)

# Get all valid route endpoints
def get_flask_routes(app):
    return {rule.endpoint for rule in app.url_map.iter_rules()}

# Find url_for usage in templates
def scan_templates(templates_dir):
    pattern = r"url_for\(['\"]([^'\"]+)['\"]"
    found = {}
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    for m in matches:
                        if m not in found:
                            found[m] = []
                        found[m].append(full_path)
    return found

# Fuzzy match broken routes and auto-fix
def fix_routes(broken, defined):
    fixed = {}
    for name, paths in broken.items():
        if name in defined:
            continue
        suggestion = difflib.get_close_matches(name, defined, n=1, cutoff=0.6)
        if suggestion:
            for path in paths:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                new_content = content.replace(f"url_for('{name}')", f"url_for('{suggestion[0]}')")
                new_content = new_content.replace(f"url_for(\"{name}\")", f"url_for(\"{suggestion[0]}\"")                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            fixed[name] = suggestion[0]
    return fixed

# Main runner
if __name__ == "__main__":
    APP_PATH = "app.py"  # Adjust if yours is in a different path
    TEMPLATES_DIR = "templates"

    print("🔍 Loading Flask app...")
    app = load_flask_app(APP_PATH)
    if not app:
        print("❌ Failed to load app. Is it defined as `app = Flask(__name__)`?")
        exit(1)

    print("✅ App loaded. Scanning...")
    defined_routes = get_flask_routes(app)
    found_routes = scan_templates(TEMPLATES_DIR)

    # Detect broken routes
    broken = {r: f for r, f in found_routes.items() if r not in defined_routes}

    if not broken:
        print("✅ All routes are valid!")
    else:
        print(f"🚨 Found {len(broken)} broken route(s). Attempting auto-fix...")
        fixed = fix_routes(broken, defined_routes)
        for b, f in fixed.items():
            print(f"🔧 Fixed: '{b}' → '{f}'")

        unfixed = set(broken) - set(fixed)
        if unfixed:
            print("❓ Unfixed routes (no good match found):")
            for u in unfixed:
                print(f"   - {u}")
