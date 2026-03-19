import os
from dotenv import load_dotenv

from secrets_manager import get_secret
from sonar_client import get_sonar_issues
from ai_fix import generate_fix
from patcher import apply_fix

load_dotenv()

SONAR_URL = os.getenv("SONAR_URL")
SONAR_PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY")
SONAR_ORG = os.getenv("SONAR_ORG")
SONAR_BRANCH = os.getenv("SONAR_BRANCH")
REPO_ROOT = "C:/Users/Compro/Projects/work/c1-2023"

def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        print("❌ Error reading file:", file_path, e)
        return []

def extract_snippet(issue, lines):
    try:
        start_line = issue["textRange"]["startLine"]

        # ✅ get all flow lines
        flow_lines = []
        for flow in issue.get("flows", []):
            for loc in flow.get("locations", []):
                flow_lines.append(loc["textRange"]["startLine"])

        # ✅ find last line
        if flow_lines:
            last_line = max(flow_lines)
        else:
            last_line = issue["textRange"]["endLine"]

        # ✅ apply logic
        start = max(1, start_line - 10)
        end = min(len(lines), last_line + 10)

        snippet = "".join(lines[start - 1:end])

        return snippet, start, end

    except Exception as e:
        print("❌ Error extracting snippet:", e)
        return "", 0, 0
        
def save_prompt_to_txt(issue, snippet, file_path, start, end):
    os.makedirs("prompts", exist_ok=True)

    file_name = f"{issue['key']}.txt"
    full_path = os.path.join("prompts", file_name)

    content = f"""
Issue Key: {issue.get("key")}
Message: {issue.get("message")}
File: {file_path}

---------------- CODE ----------------
{snippet}
--------------------------------------
"""

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("📁 Prompt saved:", full_path)

    return full_path

def read_code_snippet(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        return code
    except Exception as e:
        print("❌ Error reading file:", file_path, e)
        return ""


def run_agent():

    print("\n========== STARTING AI SONAR AGENT ==========")

    # Load secrets
    secrets = get_secret()

    OPENAI_KEY = secrets.get("OPENAI_API_KEY")
    SONAR_TOKEN = secrets.get("SONAR_API_KEY")

# ba4de1eea1444685a12bf199374bf57c712321ef
    # Fetch sonar issues
    issues = get_sonar_issues(
        SONAR_URL,
        "",
        SONAR_PROJECT_KEY,
    )

    print("Issues fetched:", len(issues))

    if not issues:
        print("\n⚠ No Sonar issues found")

        return

    for issue in issues:

        component = issue.get("component", "")

        if ":" in component:
            relative_path = component.split(":")[1]
        else:
            relative_path = component

        file_path = os.path.normpath(os.path.join(REPO_ROOT, relative_path))

        print("\nProcessing issue:", issue.get("key"))
        print("File:", file_path)

        # code = read_code_snippet(file_path)
        lines = read_file_lines(file_path)

        if not lines:
            print("⚠ Skipping, file not readable")
            continue

        snippet, start, end = extract_snippet(issue, lines)

        if not snippet:
            print("⚠ Empty snippet, skipping")
            continue

        # save prompt for debugging
        save_prompt_to_txt(issue, snippet, file_path, start, end)

        code = snippet  # 👈 send this to AI instead of full file

        if not code:
            print("⚠ Skipping, file not readable")
            continue

        print("🚀 Sending code to OpenAI...")

        # fixed_code = generate_fix(OPENAI_KEY, issue, code)
        fixed_code = "commented"

        if fixed_code == "commented":
            print("\n🛑 AGENT BLOCKED -commented")
            print("Stopping further processing.")
            break
        if fixed_code == "QUOTA_EXCEEDED":
            print("\n🛑 AGENT BLOCKED - OPENAI TOKEN LIMIT REACHED")
            print("Stopping further processing.")
            break

        if not fixed_code:
            print("⚠ AI fix failed, skipping issue")
            continue

        print("\n===== AI FIX =====")
        print(fixed_code)

        apply_fix(file_path, fixed_code)

    print("\n========== AGENT FINISHED ==========")


if __name__ == "__main__":
    run_agent()