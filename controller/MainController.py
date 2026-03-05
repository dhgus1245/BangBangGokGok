from flask import Flask, render_template, request, jsonify, Blueprint, session
from service.MainService import mainService
from service.AnalysisService import analysisService
from service.RecoService import recoService
from collections import defaultdict
import json
import os

main = Blueprint("main", __name__)

# 관심목록 데이터 파일 경로
FAVORITES_FILE = './static/json/favorites.json'

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

#index 
@main.route('/index', methods=['GET'])
def index():
    #럭셔리 아파트
    exp_apt = analysisService.expensiveApt()
    # print(exp_apt)
    #상승 확률 UP 아파트
    reg_apt = analysisService.regressionApt()
    # print(reg_apt)
    return render_template('index.html', exp_apt = exp_apt, reg_apt = reg_apt)

#매물검색
@main.route('/search', methods=['GET'])
def search():
    #매물검색 param GET
    gu = request.args.get('gu') 
    test = request.args.get('test') 
    price_ignore = request.args.get('priceIgnore') == 'on'
    price = request.args.get('priceInput')
    price = int(price) * 1000 if price and not price_ignore else 0

    pyung_raw = request.args.get('pyung')
    pyung_ignore = pyung_raw == "0" or pyung_raw is None
    pyung_map = {"1": 16, "2": 24, "3": 33}
    pyung = int(pyung_map.get(pyung_raw, 30)) if not pyung_ignore else 0

    # 연식 처리 (신축 여부)
    year_raw = request.args.get('years', '0')  # 기본값을 '0'으로 설정
    if year_raw == "5":
        year = True  # 신축만 보기
        year_ignore = False
    else:
        year = None  # 상관없음
        year_ignore = True

    # 역세권 처리
    station_raw = request.args.get('station', '0')
    station_ignore = station_raw == "0"
    station_dist = int(station_raw) if not station_ignore else None

    user_input = {
        'gu': gu,
        'price': price,
        'pyung': pyung,
        'years': year,
        'station_dist': station_dist,
        'ignore': {
            'price': price_ignore,
            'pyung': pyung_ignore,
            'years': year_ignore,
            'station': station_ignore
        }
    }
    
    # 추천 호출
    similResult = recoService.recommend_by_similarity(user_input)
    
    # 테스트 확인
    if test == "Y" :
        return render_template('test_bang.html', results=similResult)
    
    ######################################################################################
    ## 결과지역을 지도로 표시
    ######################################################################################
    similApts = list(set((item['gu'], item['dong']) for item in similResult))
    prices = [item['price'] for item in similResult if 'price' in item and item['price'] is not None]#가격
    pyungs = [item['pyung'] for item in similResult if 'pyung' in item and item['pyung'] is not None]#평수
    years = [item['years'] for item in similResult if 'years' in item and item['years'] is not None]#연식
    
    aptList = []
    coords = None
    aptCon = None
           
    # 1. 유사 지역의 지역 코드 가져오기++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    gu_dict = defaultdict(list)
    for gu, dong in similApts:  # 튜플 언패킹
        gu_dict[gu].append(dong)
    # 최종 형태로 변환 : ex [{'강북구': '미아동,번동,우이동'}]
    gu_result = [{gu: ",".join(dongs)} for gu, dongs in gu_dict.items()]

    #결과로 가져온 구로 지역번호 가져오기(Naver)++++++++++++++++++++++++++++++++++++++++++++++
    cortarList = mainService.getcortarGu(gu_result)
    # print(cortarList)
    
    #해당 구의 cortarNo의 기반으로 같은 동의 No 가져오기
    cortarDongList = mainService.getcortarDong(cortarList, gu_result)

    aptCon= {
        "priceMin" : 0,
        "priceMax" : round(max(prices))*1000 if prices else 20000000000,
        "areaMin" : round(min(pyungs) * 3.305785, 2) if pyungs else "",
        "areaMax" : round(max(pyungs) * 3.305785, 2) if pyungs else "",
        "years" : max(years) if years else ""
    } 
    
    for cortarDong in cortarDongList :
        if float(cortarDong['cortarNo']) > 0 :
            # 동번호를 통해 위치정보 가져오기
            coords = mainService.getLatLon(cortarDong)
            # 최종 아파트 리스트
            aptCon["cortarNo"] = cortarDong['cortarNo']
            aptData = mainService.getAptList(aptCon, coords)
            if aptData:
                aptList.extend(aptData[:3]) 
    

    unique_aptList = {} #아파트 중복 제거
    for item in aptList:
        complex_name = item['complexName']
        if complex_name not in unique_aptList:
            unique_aptList[complex_name] = item  # 같은 이름이 없으면 저장
    aptList = list(unique_aptList.values())
    
    if aptList : 
        return render_template('result.html', aptList = aptList, coords = coords, aptCon = aptCon)
    else :
        return render_template('result.html', aptList = [], coords = None, aptCon = None)

# 팀 소개
@main.route('/intro')
def intro():
    return render_template('intro.html')

# 아파트 매물 상세
@main.route('/sale', methods=['POST'])
def sale():
    data = request.get_json()
    aptSaleInfo = mainService.getAptSaleInfo(data['markerId'])

    return jsonify({'status': 'success', 'apt': aptSaleInfo})

@main.route('/favorites')
def favorites():
    favorites_list = load_favorites()
    return render_template('favorites.html', aptList=favorites_list)

@main.route('/add_favorite', methods=['POST'])
def add_favorite():
    apt_data = request.json
    favorites_list = load_favorites()
    
    # 이미 존재하는지 확인
    if not any(apt['markerId'] == apt_data['markerId'] for apt in favorites_list):
        favorites_list.append(apt_data)
        save_favorites(favorites_list)
        return jsonify({'success': True, 'message': '관심목록에 추가되었습니다.'})
    return jsonify({'success': False, 'message': '이미 관심목록에 존재합니다.'})

@main.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    marker_id = request.json.get('markerId')
    favorites_list = load_favorites()
    
    # 해당 아파트 제거
    favorites_list = [apt for apt in favorites_list if apt['markerId'] != marker_id]
    save_favorites(favorites_list)
    return jsonify({'success': True, 'message': '관심목록에서 제거되었습니다.'})

