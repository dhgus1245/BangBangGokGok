from flask import Flask, render_template, request, jsonify, Blueprint
from service.MainService import mainService

main = Blueprint("main", __name__)

# 매물검색 결과가져오기기
@main.route('/result', methods=['GET'])
def result():
    guNm = request.args.get('city')
    
    #이차저차 돌려서 해당 구 / 동을  가져옴

    ######################################################################################
    ## 결과지역을 지도로 표시
    ######################################################################################
    aptCon= {
        "guNm" : "서초구",
        "dongNm" : "잠원동",
        "price" : 500000,
        "houseCnt" : 2000,
        "area" : 163
    } 
    try : 
        #결과로 가져온 구로 지역번호 가져오기(Naver)
        cortarGu = mainService.getcortarGu(aptCon['guNm'])
        #cortarInfo의 cortarNo를 통해 동 번호 가져오기
        cortarDong = mainService.getcortarDong(cortarGu["cortarNo"], aptCon['dongNm'])
        if float(cortarDong['cortarNo']) > 0 :
            #동번호를 통해 위치정보 가져오기
            coords = mainService.getLatLon(cortarDong)
            #최종 아파트 리스트
            aptCon["cortarNo"] = cortarDong['cortarNo']
            aptList = mainService.getAptList(aptCon, coords)

            return render_template('result.html', aptList = aptList, coords = coords, aptCon = aptCon)
        else :
            return render_template('result.html', msg="주소가 올바르지 않습니다 : "+aptCon['dongNm'])
        
    except Exception as e:
        
        print("지도 표시 에러 : ", e)

    #f"Hello, {city}!"
    return render_template('result.html', guNm=guNm)

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

