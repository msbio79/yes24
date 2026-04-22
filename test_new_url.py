# -*- coding: utf-8 -*-
import sys, io, requests
from bs4 import BeautifulSoup
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9'
}

urls = [
    'https://www.yes24.com/Product/Category/NewProduct?categoryNumber=001&pageNumber=1&pageSize=24',
    'https://www.yes24.com/Product/Category/New?CategoryNumber=001',
    'https://www.yes24.com/Product/Category/BestSeller?categoryNumber=001&pageNumber=1&pageSize=24&orderType=NEW',
]

for url in urls:
    print(f"URL: {url}")
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    items1 = soup.select('#yesBestList li')
    items2 = soup.select('#newProductList li')
    items3 = soup.select('.itemUnit')
    print(f"  #yesBestList li: {len(items1)}")
    print(f"  #newProductList li: {len(items2)}")
    print(f"  .itemUnit: {len(items3)}")
    first_title = None
    for sel in ['#yesBestList li a.gd_name', '#newProductList li a.gd_name', '.itemUnit a.gd_name']:
        el = soup.select_one(sel)
        if el:
            first_title = el.text.strip()
            break
    print(f"  첫 번째 책: {first_title or '없음'}")
    # 페이지 제목
    title_el = soup.select_one('title')
    print(f"  페이지 제목: {title_el.text.strip() if title_el else '없음'}")
    print()
