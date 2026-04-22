# -*- coding: utf-8 -*-
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('data/books.json', encoding='utf-8') as f:
    d = json.load(f)

print("=== Yes24 크롤링 결과 확인 ===")
print(f"업데이트: {d['updated_at']}")
print(f"카테고리 수: {len(d['categories'])}")
print()

total_best = 0
total_new = 0
for cat in d['categories']:
    bs = len(cat.get('bestseller', []))
    nw = len(cat.get('new', []))
    total_best += bs
    total_new += nw
    print(f"  [{cat['name']}] 베스트 {bs}권 / 신작 {nw}권")

print()
print(f"전체: 베스트 {total_best}권 / 신작 {total_new}권")
print()

# 1위 책 샘플
cat0 = d['categories'][0]
if cat0.get('bestseller'):
    b = cat0['bestseller'][0]
    print("=== 국내도서 베스트 1위 ===")
    print(f"  제목: {b.get('title')}")
    print(f"  저자: {b.get('author')}")
    print(f"  출판사: {b.get('publisher')}")
    print(f"  가격: {b.get('price')}원")
    print(f"  링크: {b.get('link')}")

# CSV 파일 목록
csv_dir = os.path.join('data', 'csv')
csvs = os.listdir(csv_dir)
print()
print(f"=== CSV 파일 ({len(csvs)}개) ===")
for c in sorted(csvs):
    path = os.path.join(csv_dir, c)
    size = os.path.getsize(path)
    print(f"  {c}  ({size:,} bytes)")
