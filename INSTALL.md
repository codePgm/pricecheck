# 설치 가이드 (Installation Guide)

## ⚠️ 시작하기 전에

프로그램을 실행하기 전에 반드시 다음 단계를 완료해야 합니다.

---

## 📦 1단계: Python 라이브러리 설치

프로그램 폴더에서 **명령 프롬프트(CMD)** 또는 **PowerShell**을 열고:

### 방법 1: requirements.txt 사용 (권장)

```bash
pip install -r requirements.txt
```

### 방법 2: 개별 설치

```bash
pip install google-generativeai
pip install openpyxl
pip install Pillow
```

### 설치 확인

```bash
pip list | findstr google
pip list | findstr openpyxl
pip list | findstr Pillow
```

다음과 같이 표시되어야 합니다:
```
google-generativeai    0.x.x
openpyxl              3.x.x
Pillow               10.x.x
```

---

## 🔑 2단계: Google Gemini API 키 발급

### API 키 발급 절차

1. **웹사이트 접속**
   - https://makersuite.google.com/app/apikey

2. **Google 계정 로그인**
   - Gmail 계정으로 로그인

3. **API 키 생성**
   - "Create API Key" 버튼 클릭
   - API 키가 생성되면 복사 (나중에 다시 볼 수 없음!)

4. **무료 할당량 확인**
   - 하루 1500회 무료
   - 당신의 사용량: 하루 2~5회 (충분함!)

---

## ⚙️ 3단계: config.py 설정

프로그램 폴더의 `config.py` 파일을 메모장으로 열고 수정:

```python
# ==================== 필수 설정 ====================
# 기본 경로 설정
BASE_IMAGE_PATH = r"E:\code\ocrPCmaple\image"
BASE_OUTPUT_PATH = r"E:\code\ocrPCmaple\output"

# 서버 선택 (scania 또는 cllrin)
SERVER = "scania"  # "scania" 또는 "cllrin"

# 날짜 (자동으로 오늘 날짜 사용, 수동 설정도 가능)
DATE = None  # None이면 오늘 날짜 자동 사용

# Google Gemini API 키 (여기에 붙여넣기!)
GEMINI_API_KEY = "여기에_발급받은_API키를_붙여넣으세요"
```

### 주의사항
- 경로에는 `r"..."` 형식 사용 (r을 빼먹지 마세요!)
- API 키는 따옴표 안에 붙여넣기
- DATE = None으로 두면 매일 자동으로 오늘 날짜 사용

---

## ✅ 4단계: 설정 확인

```bash
python check_setup.py
```

**모든 항목이 ✓ 표시되어야 합니다!**

### 체크리스트

- [x] config.py 파일 존재
- [x] openpyxl 설치됨
- [x] google.generativeai 설치됨
- [x] PIL (Pillow) 설치됨
- [x] Gemini API 키 설정됨
- [x] 이미지 폴더 존재
- [x] 엑셀 파일 존재
- [x] 프로그램 파일들 모두 존재

---

## 🚀 5단계: 실행

설정이 완료되면:

### Windows 사용자
배치 파일 더블클릭:
- `run_scania.bat` - 스카니아 서버
- `run_cllrin.bat` - 챌린져스 서버
- `run_all.bat` - 모든 서버

### 직접 실행
```bash
python main.py
```

---

## 🐛 문제 해결

### 문제 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'google.generativeai'
```

**해결:**
```bash
pip install google-generativeai
```

### 문제 2: API 키 오류

```
ValueError: Gemini API 키가 설정되지 않았습니다.
```

**해결:**
1. config.py 열기
2. GEMINI_API_KEY에 API 키 올바르게 붙여넣기
3. 따옴표 확인

### 문제 3: 파일을 찾을 수 없음

```
FileNotFoundError: 이미지 폴더를 찾을 수 없습니다
```

**해결:**
1. config.py에서 BASE_IMAGE_PATH 확인
2. 경로에 `r"..."` 형식 사용했는지 확인
3. 폴더가 실제로 존재하는지 확인

### 문제 4: 엑셀 파일을 찾을 수 없음

```
FileNotFoundError: 엑셀 파일을 찾을 수 없습니다
```

**해결:**
1. 오늘 날짜 폴더가 존재하는지 확인
   ```
   E:\code\ocrPCmaple\output\20260216\scania\
   ```

2. 엑셀 파일 이름 확인
   ```
   최저가_20260216.xlsx
   ```

3. config.py에서 DATE 설정 확인
   - 자동: `DATE = None`
   - 수동: `DATE = "20260216"`

### 문제 5: pip 명령어를 찾을 수 없음

```
'pip'은(는) 내부 또는 외부 명령이 아닙니다
```

**해결:**
```bash
python -m pip install google-generativeai openpyxl Pillow
```

---

## 📞 추가 지원

모든 단계를 완료했는데도 문제가 있다면:

1. `check_setup.py` 실행해서 전체 메시지 복사
2. 에러 메시지 전체 복사
3. config.py 파일 내용 확인

---

## 🎉 설치 완료!

모든 단계를 완료했다면 준비 끝!

다음 단계:
1. `QUICKSTART.md` 읽기
2. 배치 파일 실행
3. 결과 확인

즐거운 메이플 생활 되세요! 🍁
