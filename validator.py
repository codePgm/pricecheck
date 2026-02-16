"""
가격 검증 로직 모듈
규칙 기반으로 의심 항목을 추출합니다.
"""

from pathlib import Path
import config
from collections import defaultdict

class Validator:
    def __init__(self, image_folder, excel_data):
        """
        Args:
            image_folder: 이미지 폴더 경로
            excel_data: ExcelHandler로 로드한 데이터
        """
        self.image_folder = Path(image_folder)
        self.excel_data = excel_data
        self.matched_items = {}
        self.suspicious_items = []
        
    def match_images_to_items(self):
        """이미지 파일명과 엑셀 아이템명 매칭"""
        if not self.image_folder.exists():
            raise FileNotFoundError(f"이미지 폴더를 찾을 수 없습니다: {self.image_folder}")
        
        # 이미지 파일 목록
        image_files = list(self.image_folder.glob("*.png"))
        
        for image_file in image_files:
            # 파일명에서 확장자 제거
            item_name = image_file.stem
            
            # 엑셀에 해당 아이템이 있는지 확인
            if item_name in self.excel_data:
                self.matched_items[item_name] = {
                    'image_path': image_file,
                    'excel_price': self.excel_data[item_name]['price'],
                    'excel_data': self.excel_data[item_name]
                }
        
        return self.matched_items
    
    def find_suspicious_items(self):
        """의심스러운 항목 찾기"""
        self.suspicious_items = []
        
        if config.ENABLE_PATTERN_CHECK:
            self._check_price_patterns()
        
        if config.ENABLE_DIGIT_CHECK:
            self._check_digit_patterns()
        
        if config.ENABLE_SERIES_CHECK:
            self._check_series_consistency()
        
        # 중복 제거 (item_name 기준)
        seen = set()
        unique_items = []
        for item in self.suspicious_items:
            if item['item_name'] not in seen:
                seen.add(item['item_name'])
                unique_items.append(item)
        
        self.suspicious_items = unique_items
        
        return self.suspicious_items
    
    def _check_price_patterns(self):
        """가격 패턴 체크"""
        for item_name, item_data in self.matched_items.items():
            price = item_data['excel_price']
            
            if price is None:
                self.suspicious_items.append({
                    'item_name': item_name,
                    'reason': '가격 정보 없음',
                    'priority': 'high'
                })
                continue
            
            # 가격을 숫자로 변환 (문자열인 경우 대비)
            try:
                price = int(price)
            except (ValueError, TypeError):
                self.suspicious_items.append({
                    'item_name': item_name,
                    'reason': '가격 형식 오류',
                    'priority': 'high'
                })
                continue
            
            # 딱 떨어지는 숫자 (예: 50000000) - 의심
            if price % 10000000 == 0 and price > 0:
                self.suspicious_items.append({
                    'item_name': item_name,
                    'reason': '딱 떨어지는 가격 (OCR 오류 가능성)',
                    'priority': 'medium'
                })
    
    def _check_digit_patterns(self):
        """자릿수 패턴 체크"""
        # 시리즈별로 그룹화
        series_groups = defaultdict(list)
        
        for item_name, item_data in self.matched_items.items():
            # 시리즈 판단
            series_name = None
            for series_key in config.ITEM_SERIES.keys():
                for keyword in config.ITEM_SERIES[series_key]:
                    if keyword in item_name:
                        series_name = series_key
                        break
                if series_name:
                    break
            
            if series_name:
                # 가격을 숫자로 변환
                price = item_data['excel_price']
                try:
                    price = int(price) if price is not None else None
                except (ValueError, TypeError):
                    price = None
                
                series_groups[series_name].append({
                    'item_name': item_name,
                    'price': price
                })
        
        # 각 시리즈 내에서 자릿수 체크
        for series_name, items in series_groups.items():
            if len(items) < 2:
                continue
            
            prices = [item['price'] for item in items if item['price'] is not None]
            if not prices:
                continue
            
            # 자릿수 계산
            digit_counts = [len(str(p)) for p in prices]
            most_common_digits = max(set(digit_counts), key=digit_counts.count)
            
            # 자릿수가 다른 아이템 찾기
            for item in items:
                if item['price'] is not None:
                    item_digits = len(str(item['price']))
                    if item_digits != most_common_digits:
                        self.suspicious_items.append({
                            'item_name': item['item_name'],
                            'reason': f'{series_name} 시리즈 자릿수 불일치 (일반: {most_common_digits}자리, 현재: {item_digits}자리)',
                            'priority': 'high'
                        })
    
    def _check_series_consistency(self):
        """시리즈별 가격 일관성 체크"""
        for series_name, price_range in config.PRICE_RANGES.items():
            min_price, max_price = price_range
            
            # 해당 시리즈 아이템 찾기
            for item_name, item_data in self.matched_items.items():
                # 시리즈에 속하는지 확인
                is_in_series = False
                for keyword in config.ITEM_SERIES.get(series_name, []):
                    if keyword in item_name:
                        is_in_series = True
                        break
                
                if not is_in_series:
                    continue
                
                price = item_data['excel_price']
                if price is None:
                    continue
                
                # 가격을 숫자로 변환
                try:
                    price = int(price)
                except (ValueError, TypeError):
                    continue
                
                # 가격 범위 벗어나는지 체크
                if price < min_price or price > max_price:
                    self.suspicious_items.append({
                        'item_name': item_name,
                        'reason': f'{series_name} 시리즈 가격 범위 벗어남 (예상: {self._format_price(min_price)}~{self._format_price(max_price)}, 현재: {self._format_price(price)})',
                        'priority': 'high'
                    })
    
    def _format_price(self, price):
        """가격 포맷팅"""
        if price >= 100000000:
            return f"{price // 100000000}억"
        elif price >= 10000:
            return f"{price // 10000}만"
        else:
            return str(price)
    
    def get_suspicious_images(self):
        """의심 항목의 이미지 경로 리스트 반환"""
        suspicious_images = []
        
        for item in self.suspicious_items:
            item_name = item['item_name']
            if item_name in self.matched_items:
                suspicious_images.append({
                    'item_name': item_name,
                    'image_path': self.matched_items[item_name]['image_path'],
                    'excel_price': self.matched_items[item_name]['excel_price'],
                    'reason': item['reason'],
                    'priority': item['priority']
                })
        
        return suspicious_images
    
    def get_stats(self):
        """통계 정보 반환"""
        return {
            'total_images': len(list(self.image_folder.glob("*.png"))),
            'matched_items': len(self.matched_items),
            'suspicious_items': len(self.suspicious_items),
            'high_priority': len([s for s in self.suspicious_items if s.get('priority') == 'high']),
            'medium_priority': len([s for s in self.suspicious_items if s.get('priority') == 'medium'])
        }
