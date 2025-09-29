# push_and_export_confluence.py
import os, sys, time, requests

BASE_SITE = os.getenv("CONFLUENCE_BASE_SITE", "https://myrrha.atlassian.net")  # no trailing slash
WIKI_BASE = f"{BASE_SITE}/wiki"
EMAIL     = os.getenv("CONFLUENCE_EMAIL")      # your Atlassian account email
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")  # from https://id.atlassian.com/manage-profile/security/api-tokens

SPACE_KEY       = os.getenv("SPACE_KEY", "YOURSPACE")   # e.g., 'MINERVA'
PARENT_PAGE_ID  = os.getenv("PARENT_PAGE_ID")           # optional: numeric Confluence pageId (parent). Leave blank to create at space root.
PAGE_TITLE      = os.getenv("PAGE_TITLE", "Cryogenic Technologies at the ESS — Extract & Notes")
BODY_FILE       = os.getenv("BODY_FILE", "ess_cryogenics_storage.html")
OUT_PDF         = os.getenv("OUT_PDF", "ESS_Cryogenics_Extract.pdf")

auth = (EMAIL, API_TOKEN)

def get_space_id(space_key: str) -> str:
    r = requests.get(f"{WIKI_BASE}/api/v2/spaces", params={"keys": space_key}, auth=auth)
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        raise SystemExit(f"Space with key '{space_key}' not found.")
    return results[0]["id"]

def create_page(space_id: str, parent_id: str|None, title: str, storage_html: str) -> str:
    body = {
        "spaceId": space_id,
        "status": "current",
        "title": title,
        "body": {"representation": "storage", "value": storage_html},
    }
    if parent_id:
        body["parentId"] = parent_id
    r = requests.post(f"{WIKI_BASE}/api/v2/pages", json=body, auth=auth)
    r.raise_for_status()
    return r.json()["id"]

def update_page(page_id: str, storage_html: str):
    body = {"body": {"representation": "storage", "value": storage_html}}
    r = requests.put(f"{WIKI_BASE}/api/v2/pages/{page_id}", json=body, auth=auth)
    r.raise_for_status()
    return page_id

def export_pdf(page_id: str, out_pdf: str):
    # FlyingPDF export (Cloud): /wiki/spaces/flyingpdf/pdfpageexport.action?pageId=...
    url = f"{WIKI_BASE}/spaces/flyingpdf/pdfpageexport.action"
    with requests.get(url, params={"pageId": page_id}, stream=True, auth=auth) as r:
        r.raise_for_status()
        with open(out_pdf, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return out_pdf

def main():
    if not (EMAIL and API_TOKEN):
        raise SystemExit("Set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN env vars.")

    with open(BODY_FILE, "r", encoding="utf-8") as f:
        storage_html = f.read()

    space_id = get_space_id(SPACE_KEY)
    parent_id = PARENT_PAGE_ID if PARENT_PAGE_ID else None

    # Create page (idempotence by title is not guaranteed; customize as needed)
    page_id = create_page(space_id, parent_id, PAGE_TITLE, storage_html)
    print(f"Created page id: {page_id}  → {WIKI_BASE}/pages/{page_id}")

    # Optional: brief wait to ensure publish before export
    time.sleep(3)

    pdf_path = export_pdf(page_id, OUT_PDF)
    print(f"PDF saved: {pdf_path}")

if __name__ == "__main__":
    main()
