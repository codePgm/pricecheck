"""
Google Gemini API를 사용한 이미지 가격 분석 모듈
"""

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from PIL import Image
import re
import config

class GeminiChecker:
    def __init__(self, api_key=None):
        """
        Args:
            api_key: Google Gemini API 키
        """
        if not GENAI_AVAILABLE:
            raise ValueError(
                "google.generativeai 라이브러리가 설치되지 않았습니다.\n"
                "다음 명령어로 설치하세요: pip install google-generativeai"
            )
        
        if api_key is None:
            api_key = config.GEMINI_API_KEY
        
        if not api_key or api_key == "AIzaSyBATGJ_hpNMkDDUKiVBVbpj32B85W32pSE": #제미나이 API 키
            raise ValueError(
                "Gemini API 키가 설정되지 않았습니다.\n"
                "config.py 파일에서 GEMINI_API_KEY를 설정해주세요.\n"
                "API 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다."
            )
        
        try:
            genai.configure(api_key=api_key)
            # gemini-1.5-flash 대신 사용 가능한 모델 사용
            # 최신 API에서는 gemini-pro-vision 또는 gemini-1.5-pro 사용
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash') #제미나이 버전
            except:
                # fallback to older model
                self.model = genai.GenerativeModel('gemini-2.5-flash') #제미나이 버전
        except Exception as e:
            raise ValueError(f"Gemini API 초기화 실패: {str(e)}")
    
    def analyze_price_image(self, image_path):
        """
        이미지에서 가격 읽기
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            dict: {
                'success': bool,
                'price': int,
                'display_text': str,
                'confidence': float,
                'raw_response': str
            }
        """
        try:
            # 이미지 열기
            image = Image.open(image_path)
            
            # Gemini에게 질문
            prompt = """
이 이미지는 메이플스토리 게임의 아이템 가격 정보입니다.
이미지에서 최저가(가장 낮은 가격)를 정확히 읽어주세요.

가격은 메소 단위이고, "5억 8000만 0000" 같은 형식으로 표시되어 있습니다.
다음 형식으로 답변해주세요:

가격: [숫자만 (예: 580000000)]
표시: [화면에 보이는 그대로 (예: 5억 8000만 0000)]
확신도: [0-100% 사이의 숫자]

반드시 위 형식을 지켜주세요.
"""
            
            # Rate limit 처리를 위한 재시도 로직
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content([prompt, image])
                    # 성공하면 파싱 후 반환
                    return self._parse_response(response.text)
                except Exception as e:
                    error_msg = str(e)
                    # Rate limit 에러인 경우
                    if '429' in error_msg or 'quota' in error_msg.lower():
                        if attempt < max_retries - 1:
                            # 마지막 시도가 아니면 재시도하지 않고 바로 실패 반환
                            # (너무 오래 기다리지 않기 위해)
                            pass
                        return {
                            'success': False,
                            'error': 'API 호출 한도 초과 (분당 5회 제한)',
                            'price': None,
                            'display_text': None,
                            'confidence': 0.0,
                            'raw_response': None
                        }
                    else:
                        # 다른 에러는 그냥 발생
                        raise
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'price': None,
                'display_text': None,
                'confidence': 0.0,
                'raw_response': None
            }
    
    def _parse_response(self, response_text):
        """Gemini 응답 파싱"""
        try:
            # 가격 추출 (숫자만)
            price_match = re.search(r'가격[:：]\s*(\d+)', response_text)
            if not price_match:
                # 대체 패턴 시도
                price_match = re.search(r'(\d{8,})', response_text)
            
            if not price_match:
                return {
                    'success': False,
                    'error': 'AI 응답에서 가격을 찾을 수 없습니다',
                    'price': None,
                    'display_text': None,
                    'confidence': 0.0,
                    'raw_response': response_text
                }
            
            price = int(price_match.group(1))
            
            # 표시 텍스트 추출
            display_match = re.search(r'표시[:：]\s*(.+?)(?:\n|확신도|$)', response_text)
            display_text = display_match.group(1).strip() if display_match else None
            
            # 확신도 추출
            confidence_match = re.search(r'확신도[:：]\s*(\d+)', response_text)
            confidence = float(confidence_match.group(1)) / 100.0 if confidence_match else 0.8
            
            return {
                'success': True,
                'price': price,
                'display_text': display_text,
                'confidence': confidence,
                'raw_response': response_text,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'응답 파싱 실패: {str(e)}',
                'price': None,
                'display_text': None,
                'confidence': 0.0,
                'raw_response': response_text
            }
    
    def batch_analyze(self, image_paths, callback=None):
        """
        여러 이미지 일괄 분석
        
        Args:
            image_paths: 이미지 경로 리스트
            callback: 진행상황 콜백 함수 (current, total, result)
            
        Returns:
            list: 분석 결과 리스트
        """
        results = []
        total = len(image_paths)
        
        for idx, image_path in enumerate(image_paths, 1):
            result = self.analyze_price_image(image_path)
            result['image_path'] = str(image_path)
            result['index'] = idx
            
            results.append(result)
            
            if callback:
                callback(idx, total, result)
        
        return results
