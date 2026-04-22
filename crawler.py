# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
Yes24 Book Crawler (v2)
- 카테고리당 100권 수집
- 가격(정가/판매가) 및 ISBN 포함
- 데이터 저장: JSON/CSV
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time
import re
from datetime import datetime, timezone, timedelta

# ── 설정 ──────────────────────────────────────────────────────────────────────
BASE_URL = "https://www.yes24.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Referer": "https://www.yes24.com",
}
DELAY = 0.5          # 요청 사이 대기 시간 (상세 페이지 요청이 많으므로 약간 줄임)
PAGE_SIZE = 100      # 한 번에 100권씩
MAX_PAGES = 1        # 1페이지(100권)만 수집

CATEGORIES = [
    {"id": "001",        "name": "국내도서 전체"},
    {"id": "001001001",  "name": "가정 살림"},
    {"id": "001001011",  "name": "건강 취미"},
    {"id": "001001025",  "name": "경제 경영"},
    {"id": "001001014",  "name": "대학교재"},
    {"id": "001001008",  "name": "만화/라이트노벨"},
    {"id": "001001022",  "name": "사회 정치"},
    {"id": "001001046",  "name": "소설/시/희곡"},
    {"id": "001001015",  "name": "수험서 자격증"},
    {"id": "001001047",  "name": "에세이"},
    {"id": "001001009",  "name": "여행"},
    {"id": "001001010",  "name": "역사"},
    {"id": "001001007",  "name": "예술"},
    {"id": "001001019",  "name": "인문"},
    {"id": "001001020",  "name": "인물"},
    {"id": "001001026",  "name": "자기계발"},
    {"id": "001001002",  "name": "자연과학"},
    {"id": "001001024",  "name": "잡지"},
    {"id": "001001021",  "name": "종교"},
    {"id": "001001005",  "name": "청소년"},
    {"id": "001001003",  "name": "IT 모바일"},
]

session = requests.Session()
session.headers.update(HEADERS)

# ── 헬퍼 ──────────────────────────────────────────────────────────────────────
def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def fetch(url):
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        print(f"  [ERROR] {url} -> {e}")
        return None

def get_isbn(goods_url):
    """상세 페이지에서 ISBN13을 가져옵니다."""
    soup = fetch(goods_url)
    if not soup:
        return ""
    isbn = ""
    # ISBN13 찾기
    for th in soup.find_all('th'):
        if 'ISBN13' in th.get_text():
            td = th.find_next_sibling('td')
            if td: isbn = clean(td.get_text())
            break
    return isbn

def make_link(href):
    if not href: return ""
    if href.startswith("/"): return BASE_URL + href
    return href

# ── 파싱 공통 ──────────────────────────────────────────────────────────────
def parse_item(li, idx, rank_offset):
    # 기본 정보
    title_el = li.select_one("a.gd_name")
    title = clean(title_el.text) if title_el else ""
    link = make_link(title_el.get("href", "")) if title_el else ""
    
    # 순위
    rank_el = li.select_one("em.ico.rank")
    rank = clean(rank_el.text) if rank_el else str(rank_offset + idx)

    # 이미지
    img_el = li.select_one("img")
    image = (img_el.get("data-original") or img_el.get("src") or "") if img_el else ""

    # 저자/출판사/날짜
    auth_el = li.select("span.info_auth a")
    author = ", ".join(clean(a.text) for a in auth_el)
    pub_el = li.select_one("span.info_pub a")
    publisher = clean(pub_el.text) if pub_el else ""
    date_el = li.select_one("span.info_date")
    pub_date = clean(date_el.text) if date_el else ""

    # 가격 (판매가/정가)
    price_sale = ""
    price_normal = ""
    sale_el = li.select_one("strong.txt_num")
    if sale_el:
        price_sale = re.sub(r"[^0-9]", "", sale_el.text)
    
    normal_el = li.select_one("span.dash")
    if normal_el:
        price_normal = re.sub(r"[^0-9]", "", normal_el.text)
    else:
        # 정가가 표시되지 않은 경우 판매가와 동일하게 처리하거나 빈값
        price_normal = price_sale

    # 평점
    rating_el = li.select_one(".info_rating em.yes_b")
    rating = clean(rating_el.text) if rating_el else ""

    # 상품 번호
    goods_no = li.get("data-goods-no", "")
    if not goods_no and link:
        m = re.search(r"/goods/(\d+)", link)
        if m: goods_no = m.group(1)

    return {
        "rank": int(rank) if rank.isdigit() else 0,
        "title": title,
        "author": author,
        "publisher": publisher,
        "pub_date": pub_date,
        "price_sale": int(price_sale) if price_sale else 0,
        "price_normal": int(price_normal) if price_normal else 0,
        "rating": rating,
        "image": image,
        "link": link,
        "goods_no": goods_no,
        "isbn": "" # 나중에 채움
    }

# ── 카테고리 크롤링 ───────────────────────────────────────────────────────────
def crawl_category(cat_id, cat_name, list_mode):
    endpoint = "BestSeller" if list_mode == "best" else "NewProduct"
    selector = "#yesBestList li" if list_mode == "best" else ".itemUnit"
    
    all_books = []
    # 100권을 위해 pageSize=100 설정
    url = f"{BASE_URL}/Product/Category/{endpoint}?categoryNumber={cat_id}&pageNumber=1&pageSize={PAGE_SIZE}"
    print(f"  [{list_mode}] {cat_name} 수집 중...")
    
    soup = fetch(url)
    if not soup: return []
    
    seen_goods = set()
    items = soup.select(selector)
    for idx, li in enumerate(items, start=1):
        book = parse_item(li, idx, 0)
        if book["title"] and book["goods_no"] not in seen_goods:
            seen_goods.add(book["goods_no"])
            
            if book["link"]:
                print(f"    ({len(seen_goods)}/100) ISBN 수집: {book['title'][:20]}...")
                book["isbn"] = get_isbn(book["link"])
                time.sleep(0.1)
                
            all_books.append(book)
            if len(all_books) >= 100: break
            
    print(f"    -> {len(all_books)}권 수집 완료")
    return all_books

# ── 저장 및 메인 ───────────────────────────────────────────────────────────
def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_csv(books, filepath):
    if not books: return
    fieldnames = ["rank", "title", "author", "publisher", "pub_date", "price_normal", "price_sale", "rating", "isbn", "link"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        # ISBN scientific notation fix for Excel
        for b in books:
            if b.get('isbn'):
                b['isbn'] = f"\t{b['isbn']}"
        writer.writerows(books)

def main():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    updated_at = now.strftime("%Y-%m-%d %H:%M")
    print(f"\n[START] Yes24 크롤러 v2 시작 - {updated_at} (KST)\n")

    result = {"updated_at": updated_at, "categories": []}
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    csv_dir = os.path.join(data_dir, "csv")
    os.makedirs(csv_dir, exist_ok=True)

    # 테스트를 위해 상위 몇 개 카테고리만 먼저 진행하거나 전체 진행
    # 전체 진행 시 시간이 꽤 소요됩니다 (약 20-30분 예상)
    for cat in CATEGORIES:
        cat_id = cat["id"]
        cat_name = cat["name"]
        print(f"\n[CAT] {cat_name}")

        best_books = crawl_category(cat_id, cat_name, "best")
        new_books  = crawl_category(cat_id, cat_name, "new")

        result["categories"].append({
            "id": cat_id,
            "name": cat_name,
            "bestseller": best_books,
            "new": new_books,
        })

        safe_name = cat_name.replace("/", "_").replace(" ", "_")
        save_csv(best_books, os.path.join(csv_dir, f"{safe_name}_best.csv"))
        save_csv(new_books,  os.path.join(csv_dir, f"{safe_name}_new.csv"))
        
        # 중간 저장 (혹시 모를 오류 대비)
        save_json(result, os.path.join(data_dir, "books.json"))

    print("\n[DONE] 모든 크롤링이 완료되었습니다!")

if __name__ == "__main__":
    main()
