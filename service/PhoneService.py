import os
import numpy as np
np.set_printoptions(suppress=True, precision=2)
import psycopg2
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from decimal import Decimal
from flask import Flask, render_template, request, jsonify, Blueprint, session
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import cv2
import logging
logger = logging.getLogger(__name__)

class PhoneService:
    
    def __init__(self):
        # 모델 경로
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        FRONT_MODEL_PATH = os.path.join(BASE_DIR, '../model/front_model.keras')
        BACK_MODEL_PATH = os.path.join(BASE_DIR, '../model/back_model.keras')
        SERIES_MODEL_PATH = os.path.join(BASE_DIR, '../model/time_series_model.keras')

        # 모델 캐싱
        self.front_model = load_model(FRONT_MODEL_PATH)
        self.back_model = load_model(BACK_MODEL_PATH)
        self.series_model = load_model(SERIES_MODEL_PATH)

        # 이미지 기본 경로
        self.image_base_dir = "/app/data/images"

    # 이미지 전처리 (OpenCV + numpy)
    def preprocess_image(self, img_path):
        safe_path = img_path.lstrip("/")  # 절대경로 방지
        full_path = os.path.join(self.image_base_dir, safe_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"{full_path} not found")

        img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"cv2.imread failed for {full_path}")

        img = cv2.resize(img, (128, 128))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=(0, -1))
        return img


    # 등급 보정
    def adjust_grade(self, grade, is_front):
        np.random.seed(123)
        rand_val = np.random.rand()
        if is_front:
            if grade == 'A' and rand_val < 0.5:
                return 'B'
        else:
            if grade == 'B' and rand_val < 0.7:
                return 'A'
        return grade

    # 이미지 등급 판별
    def estimateGrade(self, front_path, back_path):
        logger.debug("들어옴 1-1")

        grades = ['A', 'B', 'C']
        front_img = self.preprocess_image(front_path)
        back_img = self.preprocess_image(back_path)

        logger.debug(front_img)
        logger.debug(back_img)

        front_pred = self.front_model.predict(front_img)
        back_pred = self.back_model.predict(back_img)

        front_grade = self.adjust_grade(grades[np.argmax(front_pred)], True)
        back_grade = self.adjust_grade(grades[np.argmax(back_pred)], False)

        if front_grade == 'A' and back_grade == 'A':
            final_grade = 'A'
        elif front_grade in ['A','B'] and back_grade in ['A', 'B']:
            final_grade = 'B'
        else:
            final_grade = 'C'

        return {'front': front_grade, 'back': back_grade, 'grade': final_grade}

    # 예측가격 (series_model 캐싱 적용)
    def estimatePrice(self, grade_json):
        def ci(data, n_bootstrap=10000, ci=95):
            boot_means = []
            n = len(data)
            for _ in range(n_bootstrap):
                sample = np.random.choice(data, size=n, replace=True)
                boot_means.append(np.mean(sample))
            boot_means = np.array(boot_means)

            lower_percentile = (100 - ci) / 2
            upper_percentile = 100 - lower_percentile

            lower_bound = np.percentile(boot_means, lower_percentile)
            upper_bound = np.percentile(boot_means, upper_percentile)
            mean = np.mean(data)

            return mean, lower_bound, upper_bound

        # PostgreSQL 연결
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST", "postgres-db"),
            port=os.getenv("DATABASE_PORT", "5432"),
            database=os.getenv("DATABASE_NAME", "phone"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres")
        )

        model = grade_json.get("model")
        volume = grade_json.get("volume")
        grade = grade_json.get("grade")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT rp_price::float
            FROM real_price
            WHERE rp_pm_idx=%s AND rp_capacity=%s AND rp_regrade=%s
            ORDER BY rp_idx DESC
        """, (model, volume, grade))
        prices = cursor.fetchall()
        cursor.close()
        conn.close()

        price_values = [float(p[0]) for p in prices]
        result = {"result": "succ", "code": "0", "price": 0, "msg": ""}

        if len(price_values) < 5:
            return {"result": "fail", "code": "22", "msg": "판매 데이터가 적어 평균을 확인할 수 없습니다."}

        try:
            mean_price, lower_ci, upper_ci = ci(price_values)
            result["price"] = {"avg": round(mean_price, -3), "max": round(upper_ci, -3)}

            if len(price_values) >= 10:
                phone_enc = LabelEncoder().fit([model])
                cap_enc = LabelEncoder().fit([volume])
                grade_enc = LabelEncoder().fit([grade])

                future_preds = []
                seq_len = 10
                current_seq = np.array(price_values[-seq_len:]).reshape(seq_len, 1)

                for _ in range(5):
                    input_seq = current_seq.reshape(1, seq_len, 1)
                    pred = self.series_model.predict([
                        input_seq,
                        np.array([phone_enc.transform([model])[0]], dtype=np.int32),
                        np.array([cap_enc.transform([volume])[0]], dtype=np.int32),
                        np.array([grade_enc.transform([grade])[0]], dtype=np.int32)
                    ])[0, 0]
                    future_preds.append(pred)
                    current_seq = np.append(current_seq[1:], pred)

                past_prices = [p / 10000 for p in price_values[-20:]] if len(price_values) > 20 else [p / 10000 for p in price_values]
                future_prices = [round(float(p), -3)/10000 for p in future_preds]

                result["graph"] = {"result": "succ", "data": [past_prices, future_prices]}
            else:
                result["graph"] = {"result": "fail", "data": "가격 데이터 10개 미만"}

        except Exception as e:
            result.update({"result": "fail", "code": "33", "msg": f"예상금액 작업중 오류 발생: {e}"})

        return result

    
    #AI 문구생성===========================================================
    def getAiTextByApi(self, result):
        
        try :    
            # PostgreSQL 연결 -> 모델명 GET
            conn = psycopg2.connect(
                host=os.getenv("DATABASE_HOST", "postgres-db"),
                port=os.getenv("DATABASE_PORT", "5432"),
                database=os.getenv("DATABASE_NAME", "phone"),
                user=os.getenv("DATABASE_USER", "postgres"),
                password=os.getenv("DATABASE_PASSWORD", "postgres")
            )

            cursor = conn.cursor()
            
            #모델명
            sql = """
                SELECT pm_model_ko
                FROM phone_model
                WHERE pm_idx = %s
                LIMIT 1
            """        
            cursor.execute(sql, (result.get("model"),))
            model_nm = cursor.fetchone()[0]
            
            #AI_TEXT
            sql = """
                    SELECT gt_text
                    FROM gemini_template
                    ORDER BY RANDOM()
                    LIMIT 1
                """        
            cursor.execute(sql, (result.get("model"),))
            ai_text_prompt = cursor.fetchone()[0]

            cursor.close()

            conn.close() #DB연결 해제
        
            
            #Ai 문구 생성======================================================
            # API 키 설정
            genai.configure(api_key="AIzaSyD2RP_x0-or3tskYTRcjWbNHrvUjilyvZI")

            # 모델 초기화
            model = genai.GenerativeModel('gemini-1.5-flash')

            def generate_phone_ad(model_name, storage, front_condition, back_condition, price=None):

                prompt = f"""

                - 모델: {model_name}
                - 용량: {storage}
                - 앞면등급: {front_condition}등급
                - 뒷면등급: {back_condition}등급
                - 가격: {price}

                """ + ai_text_prompt

                response = model.generate_content(prompt)
                return response.text
            
            return generate_phone_ad(model_nm, result.get("volume"), result.get("front"), result.get("back"), result.get("price").get("avg"))
                
        except Exception as e:
            return f"AI 문장 생성에 실패했습니다: {e}"
        
        

phoneService = PhoneService()
