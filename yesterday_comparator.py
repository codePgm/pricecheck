"""
어제 가격 데이터 로드 및 비교 모듈
"""

from pathlib import Path
from datetime import datetime, timedelta
import openpyxl
import config


class YesterdayComparator:
    def __init__(self, server):
        """
        Args:
            server: 서버 이름 (scania 또는 cllrin)
        """
        self.server = server
        self.yesterday_data = {}
        self.yesterday_file_path = None
        
    def find_yesterday_file(self):
        """어제 엑셀 파일 찾기"""
        # 어제 날짜 계산
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y%m%d")
        
        # 어제 폴더 경로
        yesterday_folder = Path(config.BASE_OUTPUT_PATH) / yesterday_str / self.server
        
        if not yesterday_folder.exists():
            return None
        
        # 우선순위: 수정본 > 원본
        modified_file = yesterday_folder / f"최저가_{yesterday_str}_수정본.xlsx"
        original_file = yesterday_folder / f"최저가_{yesterday_str}.xlsx"
        
        if modified_file.exists():
            return modified_file
        elif original_file.exists():
            return original_file
        else:
            return None
    
    def load_yesterday_data(self):
        """어제 데이터 로드"""
        self.yesterday_file_path = self.find_yesterday_file()
        
        if self.yesterday_file_path is None:
            return False
        
        try:
            wb = openpyxl.load_workbook(self.yesterday_file_path)
            ws = wb.active
            
            for idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                if idx == 1:  # 헤더 스킵
                    continue
                
                if row[0]:  # 아이템 이름이 있는 경우만
                    item_name = row[0]
                    price = row[-1] if len(row) > 3 else None
                    
                    # 숫자로 변환
                    try:
                        price = int(price) if price is not None else None
                    except (ValueError, TypeError):
                        price = None
                    
                    self.yesterday_data[item_name] = price
            
            wb.close()
            return True
            
        except Exception as e:
            print(f"어제 파일 로드 실패: {e}")
            return False
    
    def compare_prices(self, today_data):
        """
        오늘 데이터와 어제 데이터 비교
        
        Args:
            today_data: dict - {item_name: {'price': ...}}
            
        Returns:
            list: 의심 항목 리스트
        """
        suspicious_items = []
        
        for item_name, item_info in today_data.items():
            # 오늘 가격
            today_price = item_info.get('price')
            if today_price is None:
                continue
            
            # 숫자로 변환
            try:
                today_price = int(today_price)
            except (ValueError, TypeError):
                continue
            
            # 어제 가격
            yesterday_price = self.yesterday_data.get(item_name)
            if yesterday_price is None:
                continue  # 어제 데이터 없으면 비교 불가
            
            # 가격 변동률 계산
            if yesterday_price == 0:
                continue  # 0으로 나누기 방지
            
            change_percent = abs((today_price - yesterday_price) / yesterday_price * 100)
            
            # 임계값 이상 변동 시 의심
            if change_percent >= config.PRICE_CHANGE_THRESHOLD:
                suspicious_items.append({
                    'item_name': item_name,
                    'today_price': today_price,
                    'yesterday_price': yesterday_price,
                    'change_percent': change_percent,
                    'reason': f'어제 대비 가격 {change_percent:.1f}% 변동'
                })
        
        return suspicious_items
    
    def get_stats(self):
        """통계 정보"""
        return {
            'yesterday_file': self.yesterday_file_path.name if self.yesterday_file_path else None,
            'yesterday_items': len(self.yesterday_data)
        }
