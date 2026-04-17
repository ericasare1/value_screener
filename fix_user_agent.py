import re
with open("src/value_screener/cli.py") as f:
    content = f.read()

# Smart User-Agent injection for SEC requests
def fix_request(match):
    url = match.group(1)
    return f'requests.get({url}, headers={{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}})'

# Pattern 1: requests.get("url")
content = re.sub(r'requests\.get\s*\(\s*["\']([^"\']+)["\']\s*\)', fix_request, content)

# Pattern 2: requests.get("url", ...)
content = re.sub(r'requests\.get\s*\(\s*["\']([^"\']+)["\']\s*,', lambda m: f'requests.get("{m.group(1)", headers={{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}},', content)

with open("src/value_screener/cli.py", "w") as f:
    f.write(content)
print("✅ User-Agent FIXED for SEC API!")
