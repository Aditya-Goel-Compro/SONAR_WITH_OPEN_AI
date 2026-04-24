import os
import difflib
from dotenv import load_dotenv

from secrets_manager import get_secret
from sonar_client import get_sonar_issues
from ai_fix import generate_fix
from make_PR import main as create_pr_flow

load_dotenv()

SONAR_URL = os.getenv("SONAR_URL")
SONAR_PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY")
SONAR_TOKEN = os.getenv("SONAR_TOKEN")

REPO_ROOT = "C:/Users/Compro/Projects/work/Sonar_Auto_Fix/c1-2023"

# ===============================
# 📄 Read file
# ===============================
def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []


# ===============================
# ✂ Extract context (IMPROVED)
# ===============================
def extract_context(issue, lines, window=6):
    try:
        line = issue["textRange"]["startLine"]

        start = max(1, line - window)
        end = min(len(lines), line + window)

        return "".join(lines[start - 1:end])
    except:
        return ""


# ===============================
# 🔀 Generate diff
# ===============================
def generate_diff(old_line, new_line, file_path):
    return "".join(difflib.unified_diff(
        [old_line],
        [new_line],
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    ))


# ===============================
# 🔧 Apply fix (SAFE)
# ===============================
def apply_fix(file_path, fixed_line, line_number):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        index = line_number - 1

        if index < 0 or index >= len(lines):
            print("❌ Invalid line index")
            return None

        old_line = lines[index]
        new_line = fixed_line.strip() + "\n"

        print("\n🔧 BEFORE:")
        print(old_line)

        print("🔧 AFTER:")
        print(new_line)

        lines[index] = new_line

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Fix applied safely: {file_path} (line {line_number})")

        return old_line, new_line

    except Exception as e:
        print("❌ Patch error:", e)
        return None


# ===============================
# 🧠 Rule Filter (DEMO SAFE)
# ===============================
BLOCKED_RULES = [
    "typescript:S3776",
    "javascript:S3776"
]


def is_fixable(issue):
    rule = issue.get("rule", "")

    if rule in BLOCKED_RULES:
        return False

    return True


# ===============================
# 🚀 MAIN AGENT
# ===============================
def run_agent():

    print("\n========== STARTING AI SONAR AGENT ==========")

    os.makedirs("diffs", exist_ok=True)

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

    # 🔥 Process few issues for demo
    issues = issues[:3]

    changes_applied = False

    for issue in issues:

        if not is_fixable(issue):
            print(f"⛔ Skipping rule: {issue.get('rule')}")
            continue

        component = issue.get("component", "")
        relative_path = component.split(":")[1] if ":" in component else component

        file_path = os.path.normpath(os.path.join(REPO_ROOT, relative_path))

        print("\nProcessing:", issue.get("key"))
        print("Rule:", issue.get("rule"))
        print("File:", file_path)

        lines = read_file_lines(file_path)
        if not lines:
            print("⚠ File read failed")
            continue

        line_number = issue["textRange"]["startLine"]

        if line_number <= 0 or line_number > len(lines):
            print("❌ Invalid line number")
            continue

        # 🎯 exact line to fix
        target_line = lines[line_number - 1].strip()

        # 📦 context for understanding
        context = extract_context(issue, lines)

        print("📌 Target:", target_line)

        print("🚀 Sending to AI...")

        result = generate_fix(OPENAI_KEY, issue, context, target_line)

        if result == "QUOTA_EXCEEDED":
            print("🛑 STOPPING: quota hit")
            break

        if not result or "fixed_line" not in result:
            print("⚠ Invalid AI response")
            continue

        fixed_line = result.get("fixed_line")

        # 🚨 Anti-hallucination guard
        if not fixed_line or fixed_line.strip() == target_line.strip():
            print("⚠ No valid fix → skipping")
            continue

        # 🔧 apply safe fix
        patch_result = apply_fix(file_path, fixed_line, line_number)

        if not patch_result:
            continue

        old_line, new_line = patch_result

        if old_line.strip() == new_line.strip():
            print("⚠ No meaningful change after patch")
            continue

        # 🔀 generate diff
        diff = generate_diff(old_line, new_line, relative_path)

        diff_path = os.path.join("diffs", f"{issue['key']}.patch")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff)

        print("📁 Diff saved:", diff_path)

        changes_applied = True

    print("\n========== FIXING DONE ==========")

    if changes_applied:
        print("\n🚀 Creating PR...")
        create_pr_flow()
    else:
        print("\n⚠ No changes applied, skipping PR")


if __name__ == "__main__":
    run_agent()