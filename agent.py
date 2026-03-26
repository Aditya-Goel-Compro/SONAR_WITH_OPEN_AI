import os
import difflib
from dotenv import load_dotenv

from secrets_manager import get_secret
from sonar_client import get_sonar_issues
from ai_fix import generate_fix
from patcher import apply_fix
from make_PR import main as create_pr_flow

load_dotenv()

SONAR_URL = os.getenv("SONAR_URL")
SONAR_PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY")
SONAR_TOKEN = os.getenv("SONAR_TOKEN")

REPO_ROOT = "C:/Users/Compro/Projects/work/c1-2023"


def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []


def extract_snippet(issue, lines):
    try:
        start_line = issue["textRange"]["startLine"]

        flow_lines = []
        for flow in issue.get("flows", []):
            for loc in flow.get("locations", []):
                flow_lines.append(loc["textRange"]["startLine"])

        last_line = max(flow_lines) if flow_lines else issue["textRange"]["endLine"]

        start = max(1, start_line - 10)
        end = min(len(lines), last_line + 10)

        snippet = "".join(lines[start - 1:end])

        return snippet, start, end

    except:
        return "", 0, 0


def generate_diff(old_code, new_code, file_path):
    return "".join(difflib.unified_diff(
        old_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}"
    ))


def run_agent():

    print("\n========== STARTING AI SONAR AGENT ==========")

    secrets = get_secret()
    OPENAI_KEY = secrets.get("OPENAI_API_KEY")

    issues = get_sonar_issues(
        SONAR_URL,
        SONAR_TOKEN,
        SONAR_PROJECT_KEY,
    )

    print("Issues fetched:", len(issues))

    if not issues:
        print("⚠ No Sonar issues found")
        return

    os.makedirs("diffs", exist_ok=True)

    changes_applied = False

    for issue in issues:

        component = issue.get("component", "")
        relative_path = component.split(":")[1] if ":" in component else component

        file_path = os.path.normpath(os.path.join(REPO_ROOT, relative_path))

        print("\nProcessing:", issue.get("key"))
        print("File:", file_path)

        lines = read_file_lines(file_path)
        if not lines:
            continue

        snippet, start, end = extract_snippet(issue, lines)
        if not snippet:
            continue

        print("🚀 Sending to AI...")

        result = generate_fix(OPENAI_KEY, issue, snippet)

        if result == "QUOTA_EXCEEDED":
            print("🛑 STOPPING: quota hit")
            break

        if not result or "fixed_code" not in result:
            print("⚠ Invalid AI response")
            continue

        fixed_code = result["fixed_code"]

        if fixed_code.strip() == snippet.strip():
            print("⚠ No meaningful change, skipping")
            continue

        diff = generate_diff(snippet, fixed_code, relative_path)

        diff_path = os.path.join("diffs", f"{issue['key']}.patch")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff)

        print("📁 Diff saved:", diff_path)

        apply_fix(file_path, fixed_code, start, end)

        changes_applied = True

    print("\n========== FIXING DONE ==========")

    if changes_applied:
        print("\n🚀 Creating PR...")
        create_pr_flow()
    else:
        print("\n⚠ No changes applied, skipping PR")


if __name__ == "__main__":
    run_agent()