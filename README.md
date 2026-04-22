# Yes24 도서 트렌드 뷰어 📚

Yes24 베스트셀러 & 신작 도서를 카테고리별로 크롤링해서 보여주는 정적 웹사이트입니다.  
GitHub Pages에서 바로 실행되며, 매일 GitHub Actions로 자동 갱신됩니다.

## 🌐 사이트 바로가기

> `https://<your-username>.github.io/<repo-name>/`

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 📂 카테고리 필터 | 소설, 경영, IT 등 13개 카테고리 선택 |
| 🏆 베스트셀러 | 카테고리별 Yes24 베스트셀러 순위 |
| ✨ 신작 | 카테고리별 최신 출간 도서 |
| 🔍 실시간 검색 | 제목·저자로 즉시 필터링 |
| 📥 CSV 다운로드 | 현재 카테고리·모드의 도서 목록을 CSV로 저장 |
| 🔄 자동 갱신 | GitHub Actions로 매일 오전 6시(KST) 자동 크롤링 |
| 📱 반응형 디자인 | 모바일·태블릿·데스크톱 대응 |

---

## 🚀 시작하기

### 1. 저장소 설정

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Python 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 크롤러 실행

```bash
python crawler.py
```

실행하면 `data/books.json`과 `data/csv/` 폴더에 각 카테고리 CSV 파일이 생성됩니다.

### 4. GitHub에 올리기

```bash
git add .
git commit -m "초기 데이터 추가"
git push origin main
```

### 5. GitHub Pages 설정

- 저장소 → **Settings** → **Pages**
- Source: `Deploy from a branch` → `main` 브랜치, `/ (root)` 폴더 선택
- 저장하면 `https://<username>.github.io/<repo>/` 에서 사이트 접속 가능

---

## ⚙️ GitHub Actions 자동 크롤링

`.github/workflows/crawl.yml`이 설정되어 있어:
- **매일 오전 6시(KST)** 자동으로 크롤러 실행
- 갱신된 데이터를 자동으로 커밋 & 푸시

처음 한 번은 Actions 탭에서 **workflow_dispatch**를 눌러 수동 실행하세요.

---

## 📁 프로젝트 구조

```
yes24-crawler/
├── index.html               # GitHub Pages 프론트엔드
├── crawler.py               # Yes24 크롤러
├── requirements.txt         # Python 의존성
├── data/
│   ├── books.json           # 전체 도서 데이터 (프론트엔드가 읽음)
│   └── csv/
│       ├── 소설_시_희곡_베스트셀러.csv
│       ├── 소설_시_희곡_신작.csv
│       └── ...
└── .github/
    └── workflows/
        └── crawl.yml        # 자동 크롤링 Action
```

---

## 📌 크롤링 대상 카테고리

- 국내도서 전체
- 소설/시/희곡
- 에세이
- 경제/경영
- 자기계발
- 인문학
- 사회/정치
- 역사
- 과학
- IT/컴퓨터
- 건강/취미
- 아동
- 만화/라이트노벨

---

## ⚠️ 주의사항

- 개인·비상업적 용도로만 사용하세요.
- 과도한 요청을 방지하기 위해 기본 딜레이 1초가 설정되어 있습니다.
- Yes24 사이트 구조 변경 시 크롤러 수정이 필요할 수 있습니다.

---

*데이터 출처: [Yes24](https://www.yes24.com)*
