from flask import Flask, render_template, request, jsonify, Blueprint, session
from service.PhoneService import phoneService
import tensorflow as tf
import json
import logging
logger = logging.getLogger(__name__)

phone = Blueprint("phone", __name__, url_prefix="/phone")

@phone.route('/index', methods=['GET'])
def index():

    return render_template('test_phone.html')

#매물검색
@phone.route('/api/grade', methods=['POST'])
def getPhoneGrade():
    try :
        logger.debug("들어옴")
        #앞뒤 구분값 / 이미지(encoding)
        data = request.get_json()
        front_path = data.get('front_path')
        back_path = data.get('back_path')
        logger.debug(f"1.번 front_path={front_path}, back_path={back_path}")

        
        #이미지 등급 판정
        grade_json = phoneService.estimateGrade(front_path,back_path)
        
        logger.debug(f"2.번 grade_json={grade_json}")

        grade_json['model'] = data.get('model')
        grade_json['volume'] = data.get('volume')
        
        #최종 등급 판정
        result = phoneService.estimatePrice(grade_json)
        
        logger.debug(f"3.번 result={result}")

        #결과 update
        result.update(grade_json)
        
        #ai 판매문구 생성(최종등급 판정이 완료되었을 경우에만)
        if result['result'] == "succ" :
            result["ai_text"] = phoneService.getAiTextByApi(result)

        logger.debug(f"4. 최종 결과={result}")

        # print(result)
        return jsonify(result)
        
    except Exception as e:
        print("[error] : grade 표시 에러 - c1 : ", e)
        return jsonify({'front_path':front_path, 'back_path': back_path})

