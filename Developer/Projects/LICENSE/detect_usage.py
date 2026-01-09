import requests
import csv
from difflib import SequenceMatcher
import os

# -----------------------------
# CONFIG
# -----------------------------
GITHUB_API_URL = "https://api.github.com/search/code"
# Optional: Add your GitHub token here for higher rate limits
GITHUB_TOKEN = ""  # e.g., "ghp_xxx"
PER_PAGE = 30  # Number of results per page
MAX_PAGES = 3  # How many pages to fetch
KEYWORDS = [
    "Dulsara Pieris",
    "OSAPL",
    "STAR RUNNER"
]
CSV_FILE = "license_scan_results.csv"

# Local comparison (optional)
LOCAL_FILES = ["./your_file.sh"]  # Path to your original files
REMOTE_CLONE_DIR = "./cloned_repos"  # Where to clone suspected repos for similarity check

# -----------------------------
# HEADER
# -----------------------------
headers = {
    "Accept": "application/vnd.github+json"
}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def github_search(query, per_page=30, max_pages=1):
    results = []
    for page in range(1, max_pages+1):
        params = {
            "q": query,
            "per_page": per_page,
            "page": page
        }
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"GitHub API Error: {response.status_code}, {response.text}")
            break
        data = response.json()
        results.extend(data.get("items", []))
    return results

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def local_similarity(local_path, remote_path):
    with open(local_path, "r", encoding="utf-8", errors="ignore") as f1:
        text1 = f1.read()
    with open(remote_path, "r", encoding="utf-8", errors="ignore") as f2:
        text2 = f2.read()
    return similar(text1, text2)

# -----------------------------
# MAIN SCRIPT
# -----------------------------
if __name__ == "__main__":
    query = " OR ".join(f'"{k}"' for k in KEYWORDS)
    print(f"Searching GitHub for: {query}")

    items = github_search(query, PER_PAGE, MAX_PAGES)
    print(f"Found {len(items)} results.")

    # Save to CSV
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Repo", "File Path", "URL", "Score"])
        for item in items:
            repo_name = item["repository"]["full_name"]
            file_path = item["path"]
            html_url = item["html_url"]
            score = "-"  # Placeholder for local similarity if needed

            print(f"{repo_name} → {file_path}\nURL: {html_url}\n")
            writer.writerow([repo_name, file_path, html_url, score])

    print(f"Results saved to {CSV_FILE}")

    # -----------------------------
    # OPTIONAL: Local similarity check (requires git clone)
    # -----------------------------
    if os.path.exists(REMOTE_CLONE_DIR) and LOCAL_FILES:
        for root, _, files in os.walk(REMOTE_CLONE_DIR):
            for f in files:
                remote_file = os.path.join(root, f)
                for local_file in LOCAL_FILES:
                    try:
                        score = local_similarity(local_file, remote_file)
                        if score > 0.8:  # Threshold
                            print(f"[SIMILAR] {local_file} ~ {remote_file} | Score: {score:.2f}")
                    except Exception as e:
                        pass
