import requests
from urllib.parse import urlencode


# ===============================
# ⚙️ CONFIG (EDIT ONLY THIS)
# ===============================
MAX_ISSUES = 1  # 🔥 how many issues to FIX

FETCH_PARAMS = {
    "impactSeverities": "HIGH",              # LOW / MEDIUM / HIGH
    "impactSoftwareQualities": "RELIABILITY",  # RELIABILITY / MAINTAINABILITY / SECURITY
    "issueStatuses": "OPEN",               # OPEN / CONFIRMED / etc
    "types": "CODE_SMELL",                # CODE_SMELL / BUG / VULNERABILITY
}

# 👉 OPTIONAL: allow only specific rules (leave empty for all)
ALLOWED_RULES = [
    # "typescript:S1125",
    # "typescript:S1481",
]

# 👉 ALWAYS BLOCK THESE
BLOCKED_RULES = [
    "typescript:S3776",
    "javascript:S3776"
]


# ===============================
# 🧠 Rule Filter
# ===============================
def is_safe_issue(issue):
    rule = issue.get("rule", "")

    if rule in BLOCKED_RULES:
        return False

    if ALLOWED_RULES:
        return rule in ALLOWED_RULES

    return True


# ===============================
# 🚀 Fetch Sonar Issues
# ===============================
def get_sonar_issues(sonar_url, sonar_token, project_key):

    url = f"{sonar_url}/api/issues/search"

    print("\n========== SONAR REQUEST ==========")

    params = {
        "componentKeys": project_key,
        "ps": 50,   # fetch more, filter later
        "p": 1,
        **FETCH_PARAMS
    }

    print("🌐 URL:", f"{url}?{urlencode(params)}")

    try:
        response = requests.get(
            url,
            auth=(sonar_token, ""),
            params=params,
            timeout=30
        )
    except Exception as e:
        print("❌ Request failed:", e)
        return []

    if response.status_code != 200:
        print("❌ Sonar API error")
        print(response.text)
        return []

    data = response.json()
    issues = data.get("issues", [])

    print(f"📦 Total fetched: {len(issues)}")

    # ===============================
    # 🎯 Select only required issues
    # ===============================
    selected_issues = []

    for issue in issues:

        if not is_safe_issue(issue):
            print(f"⛔ Skipped rule: {issue.get('rule')}")
            continue

        selected_issues.append(issue)

        if len(selected_issues) >= MAX_ISSUES:
            break

    print(f"\n✅ Selected Issues: {len(selected_issues)}")

    if not selected_issues:
        print("⚠ No matching issues found")

    return selected_issues