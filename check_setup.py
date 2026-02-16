"""
설정 체크 스크립트
프로그램 실행 전에 설정이 올바른지 확인합니다.
"""

import sys
from pathlib import Path

def check_setup():
    """설정 체크"""
    print("=" * 60)
    print("메이플 가격 검증 프로그램 - 설정 체크".center(60))
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. config.py 파일 존재 확인
    print("[1] config.py 파일 확인...")
    if not Path("config.py").exists():
        print("❌ config.py 파일이 없습니다!")
        all_ok = False
    else:
        print("✓ config.py 파일 존재")
        
        # config 임포트
        try:
            import config
            print("✓ config.py 정상 로드")
        except Exception as e:
            print(f"❌ config.py 로드 실패: {e}")
            all_ok = False
            return
    print()
    
    # 2. 필수 라이브러리 확인
    print("[2] 필수 라이브러리 확인...")
    libraries = [
        ("openpyxl", "엑셀 파일 처리"),
        ("google.generativeai", "Google Gemini API"),
        ("PIL", "이미지 처리")
    ]
    
    for lib_name, description in libraries:
        try:
            __import__(lib_name)
            print(f"✓ {lib_name} - {description}")
        except ImportError:
            print(f"❌ {lib_name} 없음 - {description}")
            print(f"   설치: pip install {lib_name}")
            all_ok = False
    print()
    
    # 3. API 키 확인
    print("[3] Gemini API 키 확인...")
    import config
    
    if not hasattr(config, 'GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY가 config.py에 없습니다")
        all_ok = False
    elif config.GEMINI_API_KEY == "여기에_발급받은_API키를_입력하세요":
        print("❌ API 키가 설정되지 않았습니다")
        print("   https://makersuite.google.com/app/apikey 에서 발급받으세요")
        all_ok = False
    elif len(config.GEMINI_API_KEY) < 20:
        print("⚠ API 키가 너무 짧습니다. 올바른 키인지 확인하세요")
        all_ok = False
    else:
        print(f"✓ API 키 설정됨 (길이: {len(config.GEMINI_API_KEY)})")
    print()
    
    # 4. 이미지 폴더 확인
    print("[4] 이미지 폴더 확인...")
    import config
    
    if not hasattr(config, 'IMAGE_FOLDER'):
        print("❌ IMAGE_FOLDER가 config.py에 없습니다")
        all_ok = False
    else:
        image_folder = Path(config.IMAGE_FOLDER)
        if not image_folder.exists():
            print(f"❌ 이미지 폴더를 찾을 수 없습니다: {image_folder}")
            print(f"   config.py에서 BASE_IMAGE_PATH와 SERVER를 확인하세요")
            all_ok = False
        else:
            png_files = list(image_folder.glob("*.png"))
            print(f"✓ 이미지 폴더 존재: {image_folder}")
            print(f"  - PNG 파일 개수: {len(png_files)}개")
    print()
    
    # 5. 엑셀 파일 확인
    print("[5] 엑셀 파일 확인...")
    import config
    
    if not hasattr(config, 'EXCEL_FILE'):
        print("❌ EXCEL_FILE이 config.py에 없습니다")
        all_ok = False
    else:
        excel_file = Path(config.EXCEL_FILE)
        
        if not excel_file.exists():
            print(f"❌ 엑셀 파일을 찾을 수 없습니다: {excel_file}")
            print(f"   config.py에서 BASE_OUTPUT_PATH, DATE, SERVER를 확인하세요")
            print(f"   현재 설정:")
            if hasattr(config, 'SERVER'):
                print(f"     - 서버: {config.SERVER}")
            if hasattr(config, 'DATE'):
                print(f"     - 날짜: {config.DATE}")
            all_ok = False
        else:
            print(f"✓ 엑셀 파일 존재: {excel_file}")
            
            # 엑셀 파일 읽기 테스트
            try:
                import openpyxl
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                row_count = sum(1 for row in ws.iter_rows(values_only=True) if row[0]) - 1
                print(f"  - 아이템 개수: 약 {row_count}개")
                wb.close()
            except Exception as e:
                print(f"⚠ 엑셀 파일 읽기 실패: {e}")
    print()
    
    # 6. 필수 파일 확인
    print("[6] 프로그램 파일 확인...")
    required_files = [
        "main.py",
        "excel_handler.py",
        "gemini_checker.py",
        "validator.py",
        "report_generator.py"
    ]
    
    for filename in required_files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} 없음")
            all_ok = False
    print()
    
    # 최종 결과
    print("=" * 60)
    if all_ok:
        print("✅ 모든 설정이 정상입니다!".center(60))
        print("main.py를 실행하거나 run.bat를 더블클릭하세요.".center(60))
    else:
        print("❌ 일부 설정에 문제가 있습니다.".center(60))
        print("위의 오류를 수정한 후 다시 실행하세요.".center(60))
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    try:
        result = check_setup()
        print()
        input("아무 키나 누르면 종료됩니다...")
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        print()
        input("아무 키나 누르면 종료됩니다...")
        sys.exit(1)
