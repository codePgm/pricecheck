# 여러 서버 처리 가이드

## 🎮 서버별 실행 방법

당신의 폴더 구조:
```
E:\code\ocrPCmaple\
├── image\
│   ├── scania\      (스카니아 이미지들)
│   └── cllrin\      (챌린져스 이미지들)
└── output\
    └── 20260216\
        ├── scania\  (스카니아 엑셀)
        └── cllrin\  (챌린져스 엑셀)
```

## 방법 1: config.py 수정 (간단)

### 스카니아 서버 검증
```python
# config.py
SERVER = "scania"
```
실행: `python main.py`

### 챌린져스 서버 검증
```python
# config.py
SERVER = "cllrin"
```
실행: `python main.py`

## 방법 2: 명령줄 인자 사용 (편리) - 고급

향후 업데이트로 추가 예정:
```bash
python main.py --server scania
python main.py --server cllrin
```

## 방법 3: 배치 파일 (권장)

### run_scania.bat 생성
```batch
@echo off
chcp 65001 > nul
echo ========================================
echo 스카니아 서버 가격 검증
echo ========================================
echo.

:: config.py 임시 수정 (SERVER 라인만)
python -c "import re; content=open('config.py','r',encoding='utf-8').read(); content=re.sub(r'SERVER\s*=\s*\"[^\"]*\"','SERVER = \"scania\"',content); open('config.py','w',encoding='utf-8').write(content)"

python main.py

pause
```

### run_cllrin.bat 생성
```batch
@echo off
chcp 65001 > nul
echo ========================================
echo 챌린져스 서버 가격 검증
echo ========================================
echo.

:: config.py 임시 수정
python -c "import re; content=open('config.py','r',encoding='utf-8').read(); content=re.sub(r'SERVER\s*=\s*\"[^\"]*\"','SERVER = \"cllrin\"',content); open('config.py','w',encoding='utf-8').write(content)"

python main.py

pause
```

### run_all.bat (모든 서버 순차 실행)
```batch
@echo off
chcp 65001 > nul
echo ========================================
echo 모든 서버 가격 검증
echo ========================================
echo.

echo [1/2] 스카니아 서버 검증 중...
python -c "import re; content=open('config.py','r',encoding='utf-8').read(); content=re.sub(r'SERVER\s*=\s*\"[^\"]*\"','SERVER = \"scania\"',content); open('config.py','w',encoding='utf-8').write(content)"
python main.py
echo.
echo.

echo [2/2] 챌린져스 서버 검증 중...
python -c "import re; content=open('config.py','r',encoding='utf-8').read(); content=re.sub(r'SERVER\s*=\s*\"[^\"]*\"','SERVER = \"cllrin\"',content); open('config.py','w',encoding='utf-8').write(content)"
python main.py

echo.
echo ========================================
echo 모든 서버 검증 완료!
echo ========================================
pause
```

## 📅 날짜 설정

### 오늘 날짜 자동 사용 (기본)
```python
# config.py
DATE = None  # 오늘 날짜 자동
```

### 특정 날짜 지정
```python
# config.py
DATE = "20260216"  # 2026년 2월 16일
```

이렇게 하면:
- 이미지: `E:\code\ocrPCmaple\image\scania`
- 엑셀: `E:\code\ocrPCmaple\output\20260216\scania\최저가_20260216.xlsx`

## 🎯 매일 작업 플로우 (권장)

1. **아침에 OCR 실행** → 오늘 날짜 폴더에 엑셀 생성됨
2. **스카니아 검증**: `run_scania.bat` 더블클릭
3. **챌린져스 검증**: `run_cllrin.bat` 더블클릭
4. **또는 한 번에**: `run_all.bat` 더블클릭

## 📂 결과 파일 위치

### 스카니아 실행 후
```
E:\code\ocrPCmaple\output\20260216\scania\
├── 최저가_20260216.xlsx (원본)
├── 최저가_20260216_backup.xlsx (백업)
├── 최저가_20260216_수정본.xlsx (수정됨)
└── 검증리포트_20260216.txt (리포트)
```

### 챌린져스 실행 후
```
E:\code\ocrPCmaple\output\20260216\cllrin\
├── 최저가_20260216.xlsx
├── 최저가_20260216_backup.xlsx
├── 최저가_20260216_수정본.xlsx
└── 검증리포트_20260216.txt
```

## ⚙️ 고급 설정

### 서버별 다른 가격 범위 적용

```python
# config.py

# 스카니아용 가격 범위
if SERVER == "scania":
    PRICE_RANGES = {
        "미트라": (500000000, 600000000),
    }
# 챌린져스용 가격 범위  
elif SERVER == "cllrin":
    PRICE_RANGES = {
        "미트라": (450000000, 550000000),  # 챌린져스는 더 쌈
    }
```

## 💡 팁

1. **배치 파일 사용 권장**: config.py 매번 수정하는 것보다 편함
2. **run_all.bat**: 매일 한 번만 실행하면 모든 서버 검증 완료
3. **날짜 자동**: DATE = None으로 두면 매일 자동으로 오늘 폴더 사용

## 🔍 문제 해결

### "엑셀 파일을 찾을 수 없습니다"

체크리스트:
- [ ] `BASE_OUTPUT_PATH`가 올바른가?
- [ ] `DATE` 폴더가 존재하는가?
- [ ] `SERVER` 폴더가 존재하는가?
- [ ] 엑셀 파일명이 `최저가_{DATE}.xlsx` 형식인가?

### 폴더 구조 확인
```bash
dir E:\code\ocrPCmaple\output\20260216
```
scania와 cllrin 폴더가 모두 보여야 함

### 엑셀 파일명 확인
```bash
dir E:\code\ocrPCmaple\output\20260216\scania
```
`최저가_20260216.xlsx` 파일이 있어야 함
