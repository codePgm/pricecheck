"""
메이플스토리 아이템 가격 검증 프로그램
메인 실행 파일

사용법:
    python main.py

설정 변경:
    config.py 파일에서 이미지 폴더 경로, 엑셀 파일 경로, API 키 등을 설정하세요.
"""

import sys
from pathlib import Path
from datetime import datetime
import time

import config
from excel_handler import ExcelHandler
from validator import Validator
from yesterday_comparator import YesterdayComparator
from gemini_checker import GeminiChecker
from report_generator import ReportGenerator


class PriceValidationApp:
    def __init__(self):
        self.excel_handler = None
        self.validator = None
        self.comparator = None
        self.gemini_checker = None
        self.report = ReportGenerator()
        self.start_time = None
        
    def run(self):
        """메인 실행 함수"""
        self.start_time = time.time()
        
        print("=" * 60)
        print("메이플 가격 검증 프로그램 v1.0".center(60))
        print("=" * 60)
        print()
        
        try:
            # 1. 설정 로드
            self._step1_load_config()
            
            # 2. 엑셀 데이터 로드
            self._step2_load_excel()
            
            # 3. 이미지 파일 매칭
            self._step3_match_images()
            
            # 4. 1차 검증 (규칙 기반)
            self._step4_find_suspicious()
            
            # 5. 2차 검증 (AI 분석)
            verification_results = self._step5_ai_verification()
            
            # 6. 엑셀 수정
            self._step6_fix_excel(verification_results)
            
            # 7. 리포트 생성
            self._step7_generate_report(verification_results)
            
            print()
            print("=" * 60)
            print("검증 완료!".center(60))
            self._print_summary(verification_results)
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n사용자에 의해 중단되었습니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n\n오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            if self.excel_handler:
                self.excel_handler.close()
    
    def _step1_load_config(self):
        """1단계: 설정 로드"""
        print("[1/7] 설정 로드 중...")
        
        # 서버 정보 표시
        print(f"✓ 서버: {config.SERVER}")
        print(f"✓ 날짜: {config.DATE}")
        
        # 이미지 폴더 확인
        image_folder = Path(config.IMAGE_FOLDER)
        if not image_folder.exists():
            raise FileNotFoundError(f"이미지 폴더를 찾을 수 없습니다: {image_folder}")
        print(f"✓ 이미지 폴더: {image_folder}")
        
        # 엑셀 파일 경로 확인
        excel_file = Path(config.EXCEL_FILE)
        if not excel_file.exists():
            raise FileNotFoundError(f"엑셀 파일을 찾을 수 없습니다: {excel_file}")
        print(f"✓ 엑셀 파일: {excel_file}")
        
        self.image_folder = image_folder
        self.excel_file = excel_file
        self.excel_folder = Path(config.EXCEL_FOLDER)
        print()
    
    def _step2_load_excel(self):
        """2단계: 엑셀 데이터 로드"""
        print("[2/7] 엑셀 데이터 로드 중...")
        
        self.excel_handler = ExcelHandler(self.excel_file)
        excel_data = self.excel_handler.load()
        
        print(f"✓ {len(excel_data)}개 아이템 데이터 로드 완료")
        print()
    
    def _step3_match_images(self):
        """3단계: 이미지 폴더 확인"""
        print("[3/7] 이미지 폴더 확인 중...")
        
        # 이미지 파일 개수만 확인
        png_files = list(self.image_folder.glob("*.png"))
        print(f"✓ {len(png_files)}개 이미지 파일 발견")
        print()
    
    def _step4_find_suspicious(self):
        """4단계: 어제와 가격 비교"""
        print("[4/7] 가격 변동 분석 (어제 vs 오늘)...")
        
        # YesterdayComparator 생성
        self.comparator = YesterdayComparator(config.SERVER)
        
        # 어제 파일 찾기 및 로드
        yesterday_loaded = self.comparator.load_yesterday_data()
        
        if not yesterday_loaded:
            print("⚠ 어제 파일 없음 (첫 실행 또는 파일 없음)")
            print("  → 어제 데이터와 비교할 수 없어 AI 검증을 건너뜁니다")
            print()
            self.suspicious_items = []
            return
        
        # 통계 출력
        stats = self.comparator.get_stats()
        print(f"✓ 어제 파일 발견: {stats['yesterday_file']}")
        print(f"✓ 어제 데이터 {stats['yesterday_items']}개 로드")
        
        # 가격 비교
        self.suspicious_items = self.comparator.compare_prices(self.excel_handler.data)
        
        if self.suspicious_items:
            print(f"⚠ 의심 항목 {len(self.suspicious_items)}개 발견")
            for item in self.suspicious_items[:5]:  # 최대 5개만 표시
                print(f"  · {item['item_name']}")
                print(f"    어제: {self._format_price(item['yesterday_price'])} → 오늘: {self._format_price(item['today_price'])}")
                print(f"    변동: {item['change_percent']:.1f}%")
            if len(self.suspicious_items) > 5:
                print(f"  ... 외 {len(self.suspicious_items) - 5}개")
        else:
            print("✓ 의심스러운 가격 변동 없음")
        
        print()
    
    def _step5_ai_verification(self):
        """5단계: AI 검증"""
        print("[5/7] 2차 검증 (AI 분석)...")
        
        # 의심 항목이 없으면 건너뛰기
        if not hasattr(self, 'suspicious_items') or not self.suspicious_items:
            print("✓ 검증할 의심 항목이 없습니다")
            print()
            return []
        
        # Gemini 체커 초기화
        try:
            self.gemini_checker = GeminiChecker()
        except ValueError as e:
            print(f"❌ {str(e)}")
            print()
            print("⚠ AI 검증을 건너뜁니다. API 키를 설정하면 자동 검증이 가능합니다.")
            print()
            return []
        except Exception as e:
            print(f"❌ Gemini API 초기화 오류: {str(e)}")
            print()
            return []
        
        # 콜백 함수 정의
        def progress_callback(current, total, result):
            # 대기 메시지 처리
            if result.get('waiting'):
                wait_time = result['wait_time']
                processed = result['processed']
                remaining = result['remaining']
                print()
                print(f"⏸ API 제한 방지를 위해 {wait_time}초 대기 중...")
                print(f"  (진행: {processed}/{total}, 남은 항목: {remaining}개)")
                print()
                return
            
            # 일반 진행 메시지
            item = self.suspicious_items[current - 1]
            item_name = item['item_name']
            print(f"⏳ {item_name}.png 분석 중... ({current}/{total})")
            
            if result['success']:
                ai_price = result['price']
                today_price = item['today_price']
                
                # AI 판독과 오늘 엑셀 가격 비교
                try:
                    today_price_int = int(today_price)
                except (ValueError, TypeError):
                    print(f"  → AI 판독: {self._format_price(ai_price)}")
                    print(f"  → 엑셀: {today_price} (형식 오류)")
                    print(f"  ❌ 오류 확정! (가격 형식 문제)")
                else:
                    diff_percent = abs(ai_price - today_price_int) / today_price_int * 100
                    
                    if diff_percent > config.MAX_PRICE_DIFF_PERCENT:
                        print(f"  → AI 판독: {self._format_price(ai_price)}")
                        print(f"  → 엑셀(오늘): {self._format_price(today_price_int)}")
                        print(f"  → 엑셀(어제): {self._format_price(item['yesterday_price'])}")
                        print(f"  ❌ 오류 확정! (AI와 차이: {diff_percent:.1f}%)")
                    else:
                        print(f"  → AI 판독: {self._format_price(ai_price)}")
                        print(f"  → 엑셀(오늘): {self._format_price(today_price_int)}")
                        print(f"  ✅ 정상 (오늘 가격이 맞음, 어제가 잘못됐었음)")
            else:
                error_msg = result.get('error', '알 수 없는 오류')
                print(f"  ❌ 분석 실패: {error_msg}")
            
            print()
        
        # 이미지 경로 리스트 생성
        image_paths = []
        for item in self.suspicious_items:
            image_path = self.image_folder / f"{item['item_name']}.png"
            if not image_path.exists():
                print(f"⚠ 이미지 없음: {item['item_name']}.png")
                continue
            image_paths.append(image_path)
        
        if not image_paths:
            print("❌ 검증할 이미지 파일이 없습니다")
            print()
            return []
        
        # 배치 분석 실행 (자동 대기 포함)
        print(f"총 {len(image_paths)}개 항목 검증 시작 (자동 대기 포함)")
        print()
        
        ai_results = self.gemini_checker.batch_analyze(image_paths, callback=progress_callback)
        
        # 결과 처리
        results = []
        for idx, ai_result in enumerate(ai_results):
            if idx >= len(self.suspicious_items):
                break
                
            item = self.suspicious_items[idx]
            
            result = {
                'item_name': item['item_name'],
                'excel_price': item['today_price'],
                'yesterday_price': item['yesterday_price'],
                'reason': item['reason'],
                'success': ai_result['success']
            }
            
            if ai_result['success']:
                ai_price = ai_result['price']
                confidence = ai_result['confidence']
                
                result['ai_price'] = ai_price
                result['confidence'] = confidence
                result['display_text'] = ai_result.get('display_text')
                
                # AI 가격과 오늘 엑셀 가격 비교
                try:
                    today_price_int = int(item['today_price'])
                except (ValueError, TypeError):
                    result['has_error'] = True
                else:
                    diff_percent = abs(ai_price - today_price_int) / today_price_int * 100
                    result['has_error'] = diff_percent > config.MAX_PRICE_DIFF_PERCENT
            else:
                result['error'] = ai_result.get('error', '알 수 없는 오류')
                result['has_error'] = False
            
            results.append(result)
        
        return results
    
    def _step6_fix_excel(self, verification_results):
        """6단계: 엑셀 수정"""
        print("[6/7] 엑셀 수정 중...")
        
        errors = [r for r in verification_results if r.get('has_error', False) and r.get('success', False)]
        
        if not errors:
            print("✓ 수정할 항목이 없습니다")
            print()
            return
        
        if config.AUTO_FIX:
            # 백업 생성
            if config.CREATE_BACKUP:
                backup_path = self.excel_handler.create_backup()
                print(f"✓ 백업 생성: {backup_path.name}")
            
            # 수정
            fixed_count = 0
            for result in errors:
                success = self.excel_handler.update_price(
                    result['item_name'],
                    result['ai_price'],
                    highlight=True
                )
                if success:
                    result['fixed'] = True
                    fixed_count += 1
                else:
                    result['fixed'] = False
            
            print(f"✓ {fixed_count}개 항목 수정 완료")
            
            # 저장
            output_path = self.excel_handler.save()
            print(f"✓ 저장: {output_path.name}")
            
            self.output_excel = output_path
        else:
            print("⚠ 자동 수정이 비활성화되어 있습니다 (config.AUTO_FIX = False)")
        
        print()
    
    def _step7_generate_report(self, verification_results):
        """7단계: 리포트 생성"""
        print("[7/7] 리포트 생성 중...")
        
        # 리포트 작성
        self.report.add_header(f"메이플 가격 검증 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 서버 및 비교 정보
        self.report.add_section("검증 정보")
        self.report.add_line(f"서버: {config.SERVER}")
        self.report.add_line(f"검증 날짜: {config.DATE}")
        
        if hasattr(self, 'comparator') and self.comparator:
            stats = self.comparator.get_stats()
            if stats['yesterday_file']:
                self.report.add_line(f"비교 기준: {stats['yesterday_file']}")
                self.report.add_line(f"어제 데이터: {stats['yesterday_items']}개")
        
        # 의심 항목
        if hasattr(self, 'suspicious_items') and self.suspicious_items:
            self.report.add_section("의심 항목 목록 (어제 대비 가격 변동)")
            for idx, item in enumerate(self.suspicious_items, 1):
                self.report.add_line(f"{idx}. {item['item_name']}")
                self.report.add_line(f"어제: {self._format_price(item['yesterday_price'])}", indent=1)
                self.report.add_line(f"오늘: {self._format_price(item['today_price'])}", indent=1)
                self.report.add_line(f"변동률: {item['change_percent']:.1f}%", indent=1)
                self.report.add_line("")
        
        # AI 검증 결과
        self.report.add_verification_results(verification_results)
        
        # 요약
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes}분 {seconds}초" if minutes > 0 else f"{seconds}초"
        
        total_errors = len([r for r in verification_results if r.get('has_error', False)])
        total_fixed = len([r for r in verification_results if r.get('fixed', False)])
        
        self.report.add_summary(
            total_time=time_str,
            total_checked=len(verification_results),
            total_errors=total_errors,
            total_fixed=total_fixed
        )
        
        # 파일 목록
        files = {}
        if hasattr(self, 'output_excel'):
            files['수정된 엑셀'] = self.output_excel.name
        
        report_path = self.report.save()
        files['검증 리포트'] = report_path.name
        
        self.report.add_files(files)
        
        print(f"✓ {report_path.name} 생성 완료")
        print()
    
    def _print_summary(self, verification_results):
        """요약 출력"""
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes}분 {seconds}초" if minutes > 0 else f"{seconds}초"
        
        total_checked = len(verification_results)
        total_errors = len([r for r in verification_results if r.get('has_error', False)])
        total_correct = total_checked - total_errors
        total_fixed = len([r for r in verification_results if r.get('fixed', False)])
        
        print(f"총 소요 시간: {time_str}")
        print(f"정상: {total_correct}개 / 오류: {total_errors}개 / 수정: {total_fixed}개")
        print()
        
        if hasattr(self, 'output_excel'):
            print("생성된 파일:")
            print(f"  - {self.output_excel.name}")
            
            # 리포트 경로
            excel_folder = self.excel_folder if hasattr(self, 'excel_folder') else Path(config.IMAGE_FOLDER)
            report_path = excel_folder / config.REPORT_FILE_PATTERN.format(
                date=datetime.now().strftime("%Y%m%d")
            )
            if report_path.exists():
                print(f"  - {report_path.name}")
    
    def _format_price(self, price):
        """가격 포맷팅"""
        if price is None:
            return "정보 없음"
        
        # 숫자로 변환
        try:
            price = int(price)
        except (ValueError, TypeError):
            return str(price)
        
        if price >= 100000000:
            eok = price // 100000000
            man = (price % 100000000) // 10000
            if man > 0:
                return f"{eok}억 {man}만"
            else:
                return f"{eok}억"
        elif price >= 10000:
            man = price // 10000
            return f"{man}만"
        else:
            return str(price)


def main():
    """메인 함수"""
    app = PriceValidationApp()
    app.run()


if __name__ == "__main__":
    main()
