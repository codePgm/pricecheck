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
from gemini_checker import GeminiChecker
from report_generator import ReportGenerator


class PriceValidationApp:
    def __init__(self):
        self.excel_handler = None
        self.validator = None
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
        """3단계: 이미지 파일 매칭"""
        print("[3/7] 이미지 파일 매칭 중...")
        
        self.validator = Validator(self.image_folder, self.excel_handler.data)
        matched = self.validator.match_images_to_items()
        
        print(f"✓ {len(matched)}개 이미지 파일 매칭 완료")
        
        # 매칭 안 된 이미지 확인
        all_images = set(f.stem for f in self.image_folder.glob("*.png"))
        matched_names = set(matched.keys())
        unmatched = all_images - matched_names
        
        if unmatched:
            print(f"⚠ 매칭되지 않은 이미지 {len(unmatched)}개:")
            for name in list(unmatched)[:5]:  # 최대 5개만 표시
                print(f"  - {name}")
            if len(unmatched) > 5:
                print(f"  ... 외 {len(unmatched) - 5}개")
        print()
    
    def _step4_find_suspicious(self):
        """4단계: 의심 항목 추출"""
        print("[4/7] 1차 검증 (규칙 기반)...")
        
        suspicious = self.validator.find_suspicious_items()
        
        if suspicious:
            print(f"⚠ 의심 항목 {len(suspicious)}개 발견")
            
            # 우선순위별로 표시
            high_priority = [s for s in suspicious if s.get('priority') == 'high']
            medium_priority = [s for s in suspicious if s.get('priority') == 'medium']
            
            if high_priority:
                print(f"  - 높은 우선순위: {len(high_priority)}개")
                for item in high_priority[:3]:  # 최대 3개만 표시
                    print(f"    · {item['item_name']} ({item['reason']})")
            
            if medium_priority:
                print(f"  - 중간 우선순위: {len(medium_priority)}개")
        else:
            print("✓ 의심스러운 항목이 없습니다")
        
        print()
    
    def _step5_ai_verification(self):
        """5단계: AI 검증"""
        print("[5/7] 2차 검증 (AI 분석)...")
        
        suspicious_images = self.validator.get_suspicious_images()
        
        if not suspicious_images:
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
        
        results = []
        total = len(suspicious_images)
        
        for idx, item in enumerate(suspicious_images, 1):
            print(f"⏳ {item['item_name']}.png 분석 중... ({idx}/{total})")
            
            # AI로 이미지 분석
            try:
                ai_result = self.gemini_checker.analyze_price_image(item['image_path'])
            except Exception as e:
                print(f"  ❌ 분석 중 오류: {str(e)}")
                results.append({
                    'item_name': item['item_name'],
                    'excel_price': item['excel_price'],
                    'reason': item['reason'],
                    'success': False,
                    'error': str(e)
                })
                continue
            
            result = {
                'item_name': item['item_name'],
                'excel_price': item['excel_price'],
                'reason': item['reason'],
                'success': ai_result['success']
            }
            
            if ai_result['success']:
                ai_price = ai_result['price']
                confidence = ai_result['confidence']
                
                result['ai_price'] = ai_price
                result['confidence'] = confidence
                result['display_text'] = ai_result.get('display_text')
                
                # 가격 비교
                if item['excel_price'] is None:
                    result['has_error'] = True
                    print(f"  → AI 판독: {self._format_price(ai_price)}")
                    print(f"  → 엑셀: 가격 없음")
                    print(f"  ❌ 오류 확정! (엑셀에 가격 없음)")
                else:
                    # 엑셀 가격을 숫자로 변환
                    try:
                        excel_price_int = int(item['excel_price'])
                    except (ValueError, TypeError):
                        result['has_error'] = True
                        print(f"  → AI 판독: {self._format_price(ai_price)}")
                        print(f"  → 엑셀: {item['excel_price']} (형식 오류)")
                        print(f"  ❌ 오류 확정! (가격 형식 문제)")
                    else:
                        diff_percent = abs(ai_price - excel_price_int) / excel_price_int * 100
                        
                        if diff_percent > config.MAX_PRICE_DIFF_PERCENT:
                            result['has_error'] = True
                            print(f"  → AI 판독: {self._format_price(ai_price)}")
                            print(f"  → 엑셀: {self._format_price(excel_price_int)}")
                            print(f"  ❌ 오류 확정! (차이: {diff_percent:.1f}%)")
                        else:
                            result['has_error'] = False
                            print(f"  → AI 판독: {self._format_price(ai_price)}")
                            print(f"  → 엑셀: {self._format_price(excel_price_int)}")
                            print(f"  ✅ 정상 (1차 검증 오탐)")
            else:
                result['error'] = ai_result.get('error', '알 수 없는 오류')
                result['has_error'] = False
                print(f"  ❌ 분석 실패: {result['error']}")
            
            results.append(result)
            print()
        
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
        
        # 통계
        stats = self.validator.get_stats()
        self.report.add_stats(stats)
        
        # 의심 항목
        suspicious_images = self.validator.get_suspicious_images()
        self.report.add_suspicious_items(suspicious_images)
        
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
    
    print("\n아무 키나 누르면 종료됩니다...")
    input()


if __name__ == "__main__":
    main()
