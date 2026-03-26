import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

REPO_PATH = r"C:/Users/Compro/Projects/work/c1-2023"
BRANCH_NAME = "sonarFix"
BASE_BRANCH = "env/thor"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "comprodls/c1-2023"   # ⚠️ verify this


# ===============================
# 🔧 Run Git Commands (Husky Disabled)
# ===============================
def run_cmd(cmd):
    print(f"\n👉 {cmd}")

    env = os.environ.copy()
    env["HUSKY"] = "0"   # 🔥 DISABLE HUSKY

    result = subprocess.run(cmd, shell=True, cwd=REPO_PATH, env=env)

    if result.returncode != 0:
        print("❌ Command failed:", cmd)
        exit(1)


# ===============================
# 🌿 Branch Setup
# ===============================
def prepare_branch():
    print("\n🌿 Preparing branch...")
    run_cmd(f"git checkout -B {BRANCH_NAME}")


# ===============================
# 💾 Commit Changes (Skip Hooks)
# ===============================
def commit_all_changes():
    print("\n💾 Staging changes...")

    run_cmd("git add -A")

    print("\n📝 Creating commit...")

    subprocess.run(
        'git commit -m "🔧 Sonar auto fixes" --no-verify',  # 🔥 SKIP ESLINT
        shell=True,
        cwd=REPO_PATH
    )


# ===============================
# 🚀 Push Branch
# ===============================
def push_branch():
    print("\n🚀 Pushing branch...")
    run_cmd(f"git push origin {BRANCH_NAME} --force")


# ===============================
# 🔍 Check Existing PR
# ===============================
def get_existing_pr():
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    params = {
        "head": f"{REPO_NAME.split('/')[0]}:{BRANCH_NAME}",
        "state": "open"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200 and len(response.json()) > 0:
        return response.json()[0]["html_url"]

    return None


# ===============================
# 🔥 Create PR
# ===============================
def create_pr():
    print("\n🔗 Creating Pull Request...")

    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN missing")
        return

    print("Repo:", REPO_NAME)

    existing_pr = get_existing_pr()
    if existing_pr:
        print("⚠ PR already exists:", existing_pr)
        return

    url = f"https://api.github.com/repos/{REPO_NAME}/pulls"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "title": "🔧 Sonar Auto Fixes",
        "head": BRANCH_NAME,
        "base": BASE_BRANCH,
        "body": "Automated fixes from Sonar issues"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("\n🎉 PR CREATED:", response.json()["html_url"])
    else:
        print("\n❌ PR FAILED")
        print("Status:", response.status_code)
        print(response.text)


# ===============================
# 🚀 MAIN
# ===============================
def main():
    print("\n========== LOCAL → PR ==========")

    prepare_branch()
    commit_all_changes()
    push_branch()
    create_pr()

    print("\n========== DONE ==========")


if __name__ == "__main__":
    main()