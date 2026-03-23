"""
gem_full_json_scraper.py
Scrapes bidplus.gem.gov.in/all-bids and saves full structured JSON to gem_all_bids.json.

Usage:
    python gem_full_json_scraper.py

Notes:
 - Run non-headless so you can solve CAPTCHA if needed.
 - Tweak MAX_PAGES or other options below.
"""
import json
import time
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE_LISTING = "https://bidplus.gem.gov.in/all-bids"
DOMAIN = "https://bidplus.gem.gov.in"

# ---------- configuration ----------
MAX_PAGES = 200       # max listing pages to try (tweak)
HEADLESS = False      # False recommended (solve captcha if appears)
DELAY_BETWEEN_ACTIONS = 1.0  # seconds
OUTPUT_FILE = "gem_all_bids.json"
# -----------------------------------

def setup_driver(headless=False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,1000")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # a realistic user-agent helps
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(60)
    return driver

def detect_captcha(page_source):
    s = page_source.lower()
    if "captcha" in s or "verify" in s or "recaptcha" in s or "please verify" in s:
        return True
    return False

def safe_get(driver, url, wait_seconds=8):
    try:
        driver.get(url)
    except Exception as e:
        print("Warning: page load exception:", e)
    # wait for body
    try:
        WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        pass
    time.sleep(DELAY_BETWEEN_ACTIONS)

def find_listing_detail_urls_from_listpage(html):
    """
    Extract candidate detail page URLs from a listing page HTML.
    Use heuristics: links containing /bidding/bid/ or getBidResultView etc.
    """
    soup = BeautifulSoup(html, "lxml")
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if re.search(r"/bidding/bid/|/getBidResultView/|/showbidDocument/|/bidding/bid/getBidResultView", href):
            full = urljoin(DOMAIN, href)
            if full not in urls:
                urls.append(full)
    # fallback: also include links that look like "/bidding/bid/123"
    if not urls:
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("/bidding/bid"):
                full = urljoin(DOMAIN, href)
                if full not in urls:
                    urls.append(full)
    return urls

def extract_key_values_from_soup(soup):
    """
    Try multiple heuristics to extract label->value pairs from a detail page.
    Returns dict.
    """
    data = {}

    # 1) Look for common table-like structures: tables with two columns
    for table in soup.find_all("table"):
        # try to parse rows of two cells
        for tr in table.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            if len(tds) >= 2:
                label = tds[0].get_text(" ", strip=True)
                value = tds[1].get_text(" ", strip=True)
                if label:
                    data[label] = value

    # 2) Look for definition-list style (dt/dd)
    for dl in soup.find_all(["dl"]):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            l = dt.get_text(" ", strip=True)
            v = dd.get_text(" ", strip=True)
            if l:
                data[l] = v

    # 3) Look for pairs: elements where a bold/strong label followed by text
    for strong in soup.find_all(["strong", "b"]):
        label = strong.get_text(" ", strip=True).rstrip(":")
        # next sibling text
        nxt = strong.next_sibling
        if nxt:
            txt = ""
            if isinstance(nxt, str):
                txt = nxt.strip()
            else:
                txt = getattr(nxt, "get_text", lambda s: "")(" ", strip=True)
            if label and txt:
                data[label] = txt

    # 4) Search by known label keywords and capture sibling text (heuristic)
    label_keywords = ["Bid Number", "Bid No", "Bid Start Date", "Bid Start Time", "Bid End Date",
                      "Bid End Time", "Bid Status", "Quantity", "Category", "Buyer", "Department",
                      "Bid Value", "Estimated Value", "Bid Title", "Title", "BOQ Title", "Item Name"]
    for kw in label_keywords:
        # find any element containing the kw and take nearby text
        elems = soup.find_all(text=re.compile(re.escape(kw), re.I))
        for t in elems:
            parent = t.parent
            # try sibling
            val = None
            # if parent is label-like and next sibling exists
            if parent and parent.next_sibling:
                val = parent.next_sibling.get_text(" ", strip=True) if hasattr(parent.next_sibling, "get_text") else str(parent.next_sibling).strip()
            if not val:
                # try parent parent
                pp = parent.parent if parent else None
                if pp:
                    val = pp.get_text(" ", strip=True).replace(t, "").strip()
            if val:
                data[t.strip()] = val

    return data

def extract_documents(soup):
    docs = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        txt = a.get_text(" ", strip=True)
        # heuristics: document links often include '/documentdownload' or '/showbidDocument' or end with pdf/zip
        if re.search(r"documentdownload|showbidDocument|\.pdf$|\.zip$|download", href, re.I) or "document" in href.lower():
            docs.append({
                "text": txt,
                "url": urljoin(DOMAIN, href)
            })
    # dedupe
    seen = set()
    unique = []
    for d in docs:
        if d["url"] not in seen:
            unique.append(d)
            seen.add(d["url"])
    return unique

def parse_detail_page(html, url):
    soup = BeautifulSoup(html, "lxml")
    result = {}
    result["detail_url"] = url
    # page title
    title = soup.title.get_text(strip=True) if soup.title else None
    result["page_title"] = title
    # raw short snippet
    body_text = soup.get_text(" ", strip=True)[:10000]
    result["body_snippet"] = body_text[:2000]
    # key-values heuristics
    kv = extract_key_values_from_soup(soup)
    result["fields"] = kv
    # documents
    docs = extract_documents(soup)
    result["documents"] = docs
    # try to capture BOQ / items if present in tables with headers like "S No" or "Item"
    items = []
    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
        if any(h for h in headers if re.search(r"item|description|s no|qty|quantity|rate", h)):
            # parse rows to dict
            for tr in table.find_all("tr"):
                cols = [td.get_text(" ", strip=True) for td in tr.find_all(["td","th"])]
                if len(cols) > 1:
                    items.append(cols)
    if items:
        result["items_table"] = items
    # return
    return result

def click_next_if_exists(driver):
    """
    Try to click a Next button on listing page. Heuristics: elements with text 'Next' or arrow.
    Return True if clicked and page changed, else False.
    """
    try:
        # try link text 'Next'
        elements = driver.find_elements(By.XPATH, "//a[normalize-space()='Next' or normalize-space()='NEXT' or contains(., 'Next >') or contains(., '›') ]")
        for el in elements:
            try:
                el.click()
                time.sleep(DELAY_BETWEEN_ACTIONS)
                return True
            except Exception:
                continue
        # try a button with class 'next' etc
        candidates = driver.find_elements(By.XPATH, "//a[contains(@class,'next') or contains(@class,'pagination-next') or contains(@aria-label,'Next')]")
        for c in candidates:
            try:
                c.click()
                time.sleep(DELAY_BETWEEN_ACTIONS)
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False

def main():
    driver = setup_driver(headless=HEADLESS)
    results = []
    visited_details = set()
    try:
        page_idx = 1
        safe_get(driver, BASE_LISTING)
        while page_idx <= MAX_PAGES:
            print(f"\n[+] Listing page {page_idx} -> {driver.current_url}")
            if detect_captcha(driver.page_source):
                print("!!! CAPTCHA/verification detected. Please solve it in the opened browser window.")
                input("After solving the CAPTCHA, press ENTER here to continue...")

            html = driver.page_source
            detail_urls = find_listing_detail_urls_from_listpage(html)
            print(f"  -> Found {len(detail_urls)} candidate detail URLs on page {page_idx}")

            # for each detail, open in new tab, scrape
            for durl in detail_urls:
                if durl in visited_details:
                    continue
                try:
                    print("    - opening detail:", durl)
                    # open in same tab to avoid tab management complexity
                    safe_get(driver, durl)
                    if detect_captcha(driver.page_source):
                        print("    !!! CAPTCHA on detail page. Solve it in browser.")
                        input("    After solving, press ENTER to continue...")
                    detail_html = driver.page_source
                    parsed = parse_detail_page(detail_html, durl)
                    results.append(parsed)
                    visited_details.add(durl)
                    # go back to listing page
                    driver.back()
                    time.sleep(DELAY_BETWEEN_ACTIONS)
                except Exception as e:
                    print("    Error scraping detail:", e)
                    # try to continue by going back to listing
                    try:
                        driver.get(driver.current_url)  # refresh
                    except Exception:
                        pass

            # Try to go to next page — prefer clicking Next; fallback: try ?page=...
            clicked = click_next_if_exists(driver)
            if not clicked:
                # fallback: try ?page=page_idx+1
                next_url = f"{BASE_LISTING}?page={page_idx+1}"
                print("  -> Trying fallback next URL:", next_url)
                safe_get(driver, next_url)
                # heuristic: if URL didn't change or page shows no items, break
                if page_idx >= MAX_PAGES:
                    break

            page_idx += 1

            # light sleep to be polite
            time.sleep(DELAY_BETWEEN_ACTIONS)

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # Save JSON
    print(f"\n[+] Scraped {len(results)} detail pages. Writing output to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Done.")

if __name__ == "__main__":
    main()
