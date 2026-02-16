"""
검증 결과 리포트 생성 모듈
"""

from datetime import datetime
from pathlib import Path
import config

class ReportGenerator:
    def __init__(self):
        self.report_lines = []
        
    def add_header(self, title):
        """리포트 헤더 추가"""
        separator = "=" * 60
        self.report_lines.append(separator)
        self.report_lines.append(title.center(60))
        self.report_lines.append(separator)
        self.report_lines.append("")
    
    def add_section(self, title):
        """섹션 제목 추가"""
        self.report_lines.append("")
        self.report_lines.append(f"[{title}]")
        self.report_lines.append("-" * 60)
    
    def add_line(self, text, indent=0):
        """라인 추가"""
        prefix = "  " * indent
        self.report_lines.append(f"{prefix}{text}")
    
    def add_stats(self, stats):
        """통계 정보 추가"""
        self.add_section("검증 통계")
        self.add_line(f"총 이미지 파일: {stats.get('total_images', 0)}개")
        self.add_line(f"매칭된 아이템: {stats.get('matched_items', 0)}개")
        self.add_line(f"의심 항목: {stats.get('suspicious_items', 0)}개")
        if stats.get('high_priority', 0) > 0:
            self.add_line(f"  - 높은 우선순위: {stats['high_priority']}개", indent=1)
        if stats.get('medium_priority', 0) > 0:
            self.add_line(f"  - 중간 우선순위: {stats['medium_priority']}개", indent=1)
    
    def add_suspicious_items(self, suspicious_items):
        """의심 항목 목록 추가"""
        if not suspicious_items:
            return
        
        self.add_section("의심 항목 목록")
        for idx, item in enumerate(suspicious_items, 1):
            self.add_line(f"{idx}. {item['item_name']}")
            self.add_line(f"이유: {item['reason']}", indent=1)
            self.add_line(f"우선순위: {item['priority']}", indent=1)
            if 'excel_price' in item and item['excel_price']:
                self.add_line(f"엑셀 가격: {self._format_price(item['excel_price'])}", indent=1)
            self.add_line("")
    
    def add_verification_results(self, results):
        """AI 검증 결과 추가"""
        if not results:
            return
        
        self.add_section("AI 검증 결과")
        
        errors_found = [r for r in results if r.get('has_error', False)]
        correct_items = [r for r in results if not r.get('has_error', False) and r.get('success', False)]
        failed_items = [r for r in results if not r.get('success', False)]
        
        self.add_line(f"총 검증: {len(results)}개")
        self.add_line(f"오류 발견: {len(errors_found)}개")
        self.add_line(f"정상: {len(correct_items)}개")
        if failed_items:
            self.add_line(f"검증 실패: {len(failed_items)}개")
        self.add_line("")
        
        # 오류 발견 항목 상세
        if errors_found:
            self.add_line("오류 발견 항목 상세:")
            self.add_line("")
            for idx, result in enumerate(errors_found, 1):
                self.add_line(f"{idx}. {result['item_name']}")
                
                # excel_price를 숫자로 변환
                excel_price = result['excel_price']
                try:
                    excel_price_int = int(excel_price) if excel_price is not None else None
                except (ValueError, TypeError):
                    excel_price_int = None
                
                if excel_price_int is not None:
                    self.add_line(f"엑셀 가격: {self._format_price(excel_price_int)}", indent=1)
                else:
                    self.add_line(f"엑셀 가격: {excel_price}", indent=1)
                
                self.add_line(f"실제 가격: {self._format_price(result['ai_price'])}", indent=1)
                
                # 차이 계산
                if excel_price_int is not None:
                    diff = result['ai_price'] - excel_price_int
                    diff_sign = "+" if diff > 0 else ""
                    self.add_line(f"차이: {diff_sign}{self._format_price(abs(diff))}", indent=1)
                
                if result.get('fixed', False):
                    self.add_line("수정: ✅ 완료", indent=1)
                else:
                    self.add_line("수정: ❌ 실패", indent=1)
                self.add_line("")
        
        # 검증 실패 항목
        if failed_items:
            self.add_line("검증 실패 항목:")
            self.add_line("")
            for idx, result in enumerate(failed_items, 1):
                self.add_line(f"{idx}. {result['item_name']}")
                self.add_line(f"사유: {result.get('error', '알 수 없음')}", indent=1)
                self.add_line("")
    
    def add_summary(self, total_time, total_checked, total_errors, total_fixed):
        """요약 추가"""
        self.add_section("실행 요약")
        self.add_line(f"총 소요 시간: {total_time}")
        self.add_line(f"검증 항목: {total_checked}개")
        self.add_line(f"오류 발견: {total_errors}개")
        self.add_line(f"수정 완료: {total_fixed}개")
    
    def add_files(self, files):
        """생성된 파일 목록 추가"""
        self.add_section("생성된 파일")
        for file_type, file_path in files.items():
            self.add_line(f"{file_type}: {file_path}")
    
    def _format_price(self, price):
        """가격 포맷팅"""
        if price is None:
            return "정보 없음"
        
        # 숫자로 변환
        try:
            price = int(price)
        except (ValueError, TypeError):
            return str(price)
        
        if price >= 100000000:  # 1억 이상
            eok = price // 100000000
            man = (price % 100000000) // 10000
            if man > 0:
                return f"{eok:,}억 {man:,}만"
            else:
                return f"{eok:,}억"
        elif price >= 10000:  # 1만 이상
            man = price // 10000
            rest = price % 10000
            if rest > 0:
                return f"{man:,}만 {rest:,}"
            else:
                return f"{man:,}만"
        else:
            return f"{price:,}"
    
    def generate(self):
        """리포트 텍스트 생성"""
        return "\n".join(self.report_lines)
    
    def save(self, output_path=None):
        """리포트를 파일로 저장"""
        if output_path is None:
            date_str = datetime.now().strftime("%Y%m%d")
            filename = config.REPORT_FILE_PATTERN.format(date=date_str)
            # EXCEL_FOLDER가 있으면 그곳에 저장, 없으면 IMAGE_FOLDER에 저장
            if hasattr(config, 'EXCEL_FOLDER'):
                output_path = Path(config.EXCEL_FOLDER) / filename
            else:
                output_path = Path(config.IMAGE_FOLDER) / filename
        
        report_text = self.generate()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return output_path
    
    def print(self):
        """리포트를 콘솔에 출력"""
        print(self.generate())
