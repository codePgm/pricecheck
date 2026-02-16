"""
메이플스토리 아이템 가격 OCR 검증 및 자동 수정 프로그램
이미지에서 OCR로 추출한 가격 데이터를 AI가 검증하고 오류를 자동 수정합니다.
"""

import os
import base64
from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill
import anthropic
import json
from datetime import datetime

class PriceValidator:
    def __init__(self, image_folder, excel_file, api_key=None):
        """
        Args:
            image_folder: 스크린샷 이미지들이 있는 폴더 경로
            excel_file: OCR 결과가 저장된 엑셀 파일 경로
            api_key: Anthropic API 키 (없으면 환경변수에서 가져옴)
        """
        self.image_folder = Path(image_folder)
        self.excel_file = Path(excel_file)
        
        # API 키 설정
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            # API 키는 현재 claude.ai 환경에서 자동으로 처리됨
            self.client = anthropic.Anthropic()
        
        self.errors = []
        self.corrections = []
        
    def load_excel_data(self):
        """엑셀 파일에서 데이터 로드"""
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb.active
        
        data = []
        headers = None
        
        for idx, row in enumerate(ws.iter_rows(values_only=True), 1):
            if idx == 1:
                headers = row
                continue
            
            if row[0]:  # 아이템 이름이 있는 경우만
                data.append({
                    'row