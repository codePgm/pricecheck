"""
메이플 가격 검증 프로그램 설정 파일
사용자가 여기서 경로와 설정을 변경할 수 있습니다.
"""

from datetime import datetime
import os

# ==================== 필수 설정 ====================
# 기본 경로 설정
BASE_IMAGE_PATH = r"E:\code\ocrPCmaple\image"
BASE_OUTPUT_PATH = r"E:\code\ocrPCmaple\output"

# 서버 선택 (scania 또는 cllrin)
# 환경 변수 SERVER_NAME이 있으면 그것을 우선 사용 (배치 파일용)
SERVER = os.getenv('SERVER_NAME', 'scania')  # 기본값: scania

# 날짜 (자동으로 오늘 날짜 사용, 수동 설정도 가능)
# 자동: None (오늘 날짜)
# 수동: "20260216" 같은 형식
DATE = None  # None이면 오늘 날짜 자동 사용

# ==================== 자동 경로 생성 ====================
# 날짜 설정
if DATE is None:
    DATE = datetime.now().strftime("%Y%m%d")

# 이미지 폴더 경로
IMAGE_FOLDER = rf"{BASE_IMAGE_PATH}\{SERVER}"

# 엑셀 파일 경로
EXCEL_FOLDER = rf"{BASE_OUTPUT_PATH}\{DATE}\{SERVER}"
EXCEL_FILE = rf"{EXCEL_FOLDER}\최저가_{DATE}.xlsx"

# ==================== Google Gemini API 키 ====================
# 서버별로 다른 API 키 사용 (분당 5회 제한을 피하기 위해)
# 각 서버마다 다른 Google 계정으로 API 키를 발급받으세요
API_KEYS = {
    "scania": "여기에_스카니아용_API키_입력",
    "cllrin": "여기에_챌린져스용_API키_입력"
}

# 현재 서버의 API 키 자동 선택
GEMINI_API_KEY = API_KEYS.get(SERVER, "여기에_발급받은_API키를_입력하세요")

# ==================== 고급 설정 ====================
# AI 확신도 임계값 (0.0 ~ 1.0, 높을수록 엄격)
CONFIDENCE_THRESHOLD = 0.8

# 가격 차이 허용 범위 (%) - 이 이상 차이나면 의심 항목으로 분류
MAX_PRICE_DIFF_PERCENT = 10

# 어제 대비 가격 변동 임계값 (%) - 의심 아이템 검증
PRICE_CHANGE_THRESHOLD = 50  # 어제 대비 50% 이상 변동 시 의심

# 자동 수정 여부
AUTO_FIX = True

# 백업 파일 생성 여부
CREATE_BACKUP = True

# 의심 항목 감지 규칙 활성화
ENABLE_PATTERN_CHECK = True  # 같은 시리즈 가격 패턴 체크
ENABLE_DIGIT_CHECK = True     # 자릿수 체크
ENABLE_SERIES_CHECK = True    # 시리즈별 비교 체크

# 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# ==================== 시리즈 정의 ====================
# 같은 시리즈끼리 묶어서 가격 비교에 사용
ITEM_SERIES = {
    "에테르넬": ["에테르넬"],
    "미트라": ["미트라의 분노"],
    "저주받은": ["저주받은"],
}

# 각 시리즈의 예상 가격 범위 (자동 감지도 가능하지만 수동 설정 가능)
PRICE_RANGES = {
    "에테르넬": (90000000, 2500000000),      # 9천만 ~ 25억
    "미트라": (500000000, 600000000),        # 5억 ~ 6억
    "저주받은": (4600000000, 4900000000),    # 46억 ~ 49억
}

# ==================== 출력 설정 ====================
# 수정된 엑셀 파일명 패턴
OUTPUT_EXCEL_PATTERN = "{original_name}_수정본.xlsx"

# 백업 파일명 패턴
BACKUP_EXCEL_PATTERN = "{original_name}_backup.xlsx"

# 리포트 파일명 패턴
REPORT_FILE_PATTERN = "검증리포트_{date}.txt"

# 수정된 셀 하이라이트 색상 (RGB)
HIGHLIGHT_COLOR = "FFFF00"  # 노란색
