import os
import re
import importlib.util
from flask import Flask

# === CONFIG ===
FLASK_APP_PATH = "app.py"  # or wherever your Flask app starts
TEMPLATE_DIR = "templates"

def get_flask_routes(app):
    endpoints = set()
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.add(rule.endpoint)
    return endpoints

def extract_url_for_calls(template_dir):
    pattern = re.compile(r"url_for\(['\"]([\w\.]+)['\"]")
    found_endpoints = set()

    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                with open(os.path.join(root, file), encoding='utf-8') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    found_endpoints.update(matches)
    return found_endpoints

def load_flask_app():
    spec = importlib.util.spec_from_file_location("flask_app", FLASK_APP_PATH)
    flask_app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flask_app_module)
    app = getattr(flask_app_module, 'app', None)
    if not isinstance(app, Flask):
        raise Exception("Flask app not found or 'app' variable not defined in your app file.")
    return app

if __name__ == "__main__":
    print("🔍 Loading Flask app...")
    app = load_flask_app()
    print("✅ App loaded. Scanning...")

    defined_endpoints = get_flask_routes(app)
    used_endpoints = extract_url_for_calls(TEMPLATE_DIR)

    print(f"\n📂 Found {len(defined_endpoints)} defined endpoints in Flask")
    print(f"📄 Found {len(used_endpoints)} url_for calls in templates")

    broken = used_endpoints - defined_endpoints
    if broken:
        print("\n🚨 Broken or missing endpoints:")
        for b in sorted(broken):
            print(f"  - {b}")
    else:
        print("\n✅ All url_for() calls are valid!")

