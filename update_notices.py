import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def update_notices():
    # 1. 기존 data.json 파일 읽기
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("에러: data.json 파일을 찾을 수 없습니다.")
        return

    businesses = data.get("businesses", [])
    keyword_map = {b["id"]: b["keywords"] for b in businesses}

    if "notices" not in data:
        data["notices"] = {b["id"]: [] for b in businesses}

    # 2. KYWA 공지사항 목록 크롤링
    url = "https://www.kywa.or.kr/pressinfo/notice_list.jsp"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"웹페이지 접속 에러: {e}")
        return

    trs = soup.select("table tbody tr")

    # 3. 데이터 추출 및 키워드 매칭
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) < 5:
            continue
        
        a_tag = tds[1].find('a')
        if not a_tag:
            continue
            
        title = a_tag.get('title', '').strip()
        if not title:
            title = a_tag.text.strip()
            
        href = a_tag.get('href', '')
        full_url = urljoin(url, href)
        
        # 고유 번호(no) 추출
        notice_id = ""
        if "no=" in href:
            notice_id = href.split("no=")[1].split("&")[0]
            
        author = tds[2].text.strip()
        date = tds[3].text.strip()
        
        # 설정된 키워드와 제목 비교
        for b_id, keywords in keyword_map.items():
            matched = [kw for kw in keywords if kw in title]
            if matched:
                new_notice = {
                    "id": notice_id,
                    "title": title,
                    "date": date,
                    "author": author,
                    "url": full_url,
                    "matchedKeywords": matched
                }
                
                # 중복 저장 방지
                if b_id not in data["notices"]:
                    data["notices"][b_id] = []
                    
                existing_ids = [n["id"] for n in data["notices"][b_id]]
                if notice_id not in existing_ids:
                    data["notices"][b_id].append(new_notice)

    # 4. 갱신된 데이터를 data.json에 덮어쓰기
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("크롤링 및 data.json 업데이트가 완료되었습니다.")

if __name__ == "__main__":
    update_notices()