import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

# =====================================================================
# CONFIGURATION FROM ENVIRONMENT VARIABLES
# =====================================================================
YOUTRACK_BASE_URL = os.environ.get("YOUTRACK_BASE_URL", "").rstrip('/')
YOUTRACK_TOKEN = os.environ.get("YOUTRACK_TOKEN", "")
YOUTRACK_PROJECT_ID = os.environ.get("YOUTRACK_PROJECT_ID", "PHY")

# In GitHub Actions, GITHUB_REPOSITORY is automatically set to "owner/repo"
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "YusufSemihCan/Physics-Simulator")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def make_request(url, headers, method="GET", data=None):
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return None
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8', errors='ignore')
        print(f"[-] HTTP Error {e.code} for {url}:\n{error_content}")
        return None

def get_youtrack_issues():
    print(f"[*] Fetching unresolved issues from YouTrack project '{YOUTRACK_PROJECT_ID}'...")
    query = urllib.parse.quote(f"project: {YOUTRACK_PROJECT_ID} #Unresolved")
    fields = "idReadable,summary,description"
    url = f"{YOUTRACK_BASE_URL}/api/issues?query={query}&fields={fields}"
    
    headers = {
        "Authorization": f"Bearer {YOUTRACK_TOKEN}",
        "Accept": "application/json"
    }
    
    issues = make_request(url, headers)
    return issues or []

def get_existing_github_issues():
    print("[*] Checking existing GitHub issues to avoid duplicates...")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=all&per_page=100"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    issues = make_request(url, headers)
    if not issues:
        return set()
    
    existing_yt_ids = set()
    for issue in issues:
        title = issue.get("title", "")
        if title.startswith("[") and "]" in title:
            possible_id = title[1:title.index("]")]
            existing_yt_ids.add(possible_id)
            
    return existing_yt_ids

def create_github_issue(yt_id, summary, description):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    title = f"[{yt_id}] {summary}"
    body = f"{description or ''}\n\n---\n*Migrated automatically from YouTrack issue: {yt_id}*"
    
    payload = {
        "title": title,
        "body": body
    }
    
    res = make_request(url, headers, method="POST", data=payload)
    if res and "html_url" in res:
        print(f"[+] Successfully created GitHub issue: {res['html_url']}")
    else:
        print(f"[-] Failed to create GitHub issue for {yt_id}")

# =====================================================================
# MAIN ROUTINE
# =====================================================================
def main():
    if not YOUTRACK_BASE_URL or not YOUTRACK_TOKEN or not GITHUB_TOKEN:
        print("[!] Missing required environment variables (YOUTRACK_BASE_URL, YOUTRACK_TOKEN, GITHUB_TOKEN).")
        sys.exit(1)

    yt_issues = get_youtrack_issues()
    print(f"[*] Found {len(yt_issues)} unresolved YouTrack issue(s).")
    
    if not yt_issues:
        return

    existing_github_ids = get_existing_github_issues()
    
    created_count = 0
    for issue in yt_issues:
        yt_id = issue.get("idReadable")
        summary = issue.get("summary", "No Summary")
        description = issue.get("description", "")
        
        if yt_id in existing_github_ids:
            print(f"[*] Skipping {yt_id} (already exists on GitHub).")
            continue
            
        print(f"[*] Importing {yt_id}: {summary}...")
        create_github_issue(yt_id, summary, description)
        created_count += 1

    print(f"[*] Sync finished. Imported {created_count} new issue(s).")

if __name__ == "__main__":
    main()
