import os
import json
from datetime import datetime
from pathlib import Path

# 파일 크기를 읽기 좋은 단위(KB, MB 등)로 변환하는 함수
def format_file_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_in_bytes >= 1024 and i < len(size_name) - 1:
        size_in_bytes /= 1024.0
        i += 1
        
    # 소수점 첫째 자리까지 표시 (예: 1.5MB)
    # KB 단위이고 100KB 이상일 경우 소수점 없이 표시하는 등 취향껏 수정 가능합니다.
    if size_name[i] == "B" or size_name[i] == "KB":
        return f"{int(size_in_bytes)}{size_name[i]}"
    return f"{size_in_bytes:.1f}{size_name[i]}"

def generate_resource_json(target_folder_path):
    resources = []
    base_path = Path(target_folder_path)
    
    # 오늘 날짜 (YYYY-MM-DD)
    today_date = datetime.now().strftime("%Y-%m-%d")

    # 대상 폴더가 존재하지 않으면 오류 메시지 출력
    if not base_path.exists() or not base_path.is_dir():
        print(f"오류: '{target_folder_path}' 폴더를 찾을 수 없습니다. 폴더 경로를 확인해주세요.")
        return resources

    # 폴더 내의 모든 파일 순회 (하위 폴더 포함)
    for file_path in base_path.rglob('*'):
        if file_path.is_file():
            # 1. 파일명 추출 (확장자 제외)
            title = file_path.stem
            
            # 2. 파일 타입 추출 (확장자를 대문자로, . 떼고)
            file_type = file_path.suffix.lstrip('.').upper()
            if not file_type:
                file_type = "UNKNOWN"
                
            # 3. 파일 크기 추출 및 변환
            size_in_bytes = file_path.stat().st_size
            file_size_formatted = format_file_size(size_in_bytes)
            
            # (옵션) 4. 폴더 구조를 기반으로 business와 category 유추
            # 예: target_folder/volunteer/law/문서.pdf 라면
            # business = 'volunteer', category = 'law' 로 자동 배정
            parts = file_path.relative_to(base_path).parts
            business = parts[0] if len(parts) > 0 else "unknown"
            category = parts[1] if len(parts) > 1 else "unknown"

            # 5. JSON 딕셔너리 구성
            resource_item = {
                "business": business,
                "category": category,
                "title": title,
                "registeredAt": today_date,
                "audience": ["공통"], # 필요 시 수정
                "keywords": ["키워드입력"], # 필요 시 수정
                "description": "자료에 대한 설명을 입력해주세요.", # 필요 시 수정
                "fileType": file_type,
                "fileSize": file_size_formatted,
                "downloadUrl": f"<!-----------여기에 {title}.{file_type.lower()} 링크가 들어가야함------------------>",
                "isNew": True
            }
            resources.append(resource_item)
            
    return resources

if __name__ == "__main__":
    # 파일을 읽어올 기준 폴더 이름을 설정하세요.
    # 스크립트 파일과 같은 위치에 'resources'라는 폴더가 있다고 가정합니다.
    TARGET_DIR = "./resources" 
    
    print(f"'{TARGET_DIR}' 폴더 안의 파일들을 분석합니다...\n")
    
    extracted_data = generate_resource_json(TARGET_DIR)
    
    if extracted_data:
        # JSON 형태로 이쁘게 출력 (들여쓰기 2칸, 한글 깨짐 방지)
        json_output = json.dumps(extracted_data, ensure_ascii=False, indent=2)
        
        # 결과를 화면에 출력
        print(json_output)
        
        # 결과를 output.json 파일로 저장 (원하시면 주석 해제)
        with open("output.json", "w", encoding="utf-8") as f:
            f.write(json_output)
        print("\n✅ 분석 완료! 결과가 'output.json' 파일로 저장되었습니다.")
        print("이제 필요한 URL과 세부 내용만 엑셀이나 편집기에서 채워 넣으시면 됩니다.")
