from urllib.request import urlopen
import requests
import urllib.parse  
import time, random

class MainService:
    #구 번호(cortarNo) 가져오기

    def getNaverApi(self, url, max_retries=5):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://new.land.naver.com/",
            "Origin": "https://new.land.naver.com",
        }
        retry_delay = 1
        
        for attempt in range(max_retries):
            time.sleep(random.uniform(1.0, 2.0))  # 기본 지연
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 429:  # Too Many Requests
                    print(f"429 error, retrying after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                else:
                    print(f"HTTP error: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request exception: {e}")
                break
        
        return None

    def getcortarGu(self, gu_result):
        
        gu_map = {
            "강남구": {"cortarNo": "1168000000", "centerLat": 37.517408, "centerLon": 127.047313, "cortarType": "dvsn"},
            "강동구": {"cortarNo": "1174000000", "centerLat": 37.530126, "centerLon": 127.123771, "cortarType": "dvsn"},
            "강북구": {"cortarNo": "1130500000", "centerLat": 37.63974, "centerLon": 127.025488, "cortarType": "dvsn"},
            "강서구": {"cortarNo": "1150000000", "centerLat": 37.550985, "centerLon": 126.849534, "cortarType": "dvsn"},
            "관악구": {"cortarNo": "1162000000", "centerLat": 37.481021, "centerLon": 126.951601, "cortarType": "dvsn"},
            "광진구": {"cortarNo": "1121500000", "centerLat": 37.538617, "centerLon": 127.082375, "cortarType": "dvsn"},
            "구로구": {"cortarNo": "1153000000", "centerLat": 37.49551, "centerLon": 126.887532, "cortarType": "dvsn"},
            "금천구": {"cortarNo": "1154500000", "centerLat": 37.45196, "centerLon": 126.902075, "cortarType": "dvsn"},
            "노원구": {"cortarNo": "1135000000", "centerLat": 37.654286, "centerLon": 127.056411, "cortarType": "dvsn"},
            "도봉구": {"cortarNo": "1132000000", "centerLat": 37.668768, "centerLon": 127.047163, "cortarType": "dvsn"},
            "동대문구": {"cortarNo": "1123000000", "centerLat": 37.574493, "centerLon": 127.039765, "cortarType": "dvsn"},
            "동작구": {"cortarNo": "1159000000", "centerLat": 37.51245, "centerLon": 126.9395, "cortarType": "dvsn"},
            "마포구": {"cortarNo": "1144000000", "centerLat": 37.563517, "centerLon": 126.9084, "cortarType": "dvsn"},
            "서대문구": {"cortarNo": "1141000000", "centerLat": 37.579225, "centerLon": 126.9368, "cortarType": "dvsn"},
            "서초구": {"cortarNo": "1165000000", "centerLat": 37.483564, "centerLon": 127.032594, "cortarType": "dvsn"},
            "성동구": {"cortarNo": "1120000000", "centerLat": 37.563475, "centerLon": 127.036838, "cortarType": "dvsn"},
            "성북구": {"cortarNo": "1129000000", "centerLat": 37.5874, "centerLon": 127.020729, "cortarType": "dvsn"},
            "송파구": {"cortarNo": "1171000000", "centerLat": 37.514592, "centerLon": 127.105863, "cortarType": "dvsn"},
            "양천구": {"cortarNo": "1147000000", "centerLat": 37.517007, "centerLon": 126.866546, "cortarType": "dvsn"},
            "영등포구": {"cortarNo": "1156000000", "centerLat": 37.526367, "centerLon": 126.896213, "cortarType": "dvsn"},
            "용산구": {"cortarNo": "1117000000", "centerLat": 37.538825, "centerLon": 126.96535, "cortarType": "dvsn"},
            "은평구": {"cortarNo": "1138000000", "centerLat": 37.60278, "centerLon": 126.929163, "cortarType": "dvsn"},
            "종로구": {"cortarNo": "1111000000", "centerLat": 37.573025, "centerLon": 126.979638, "cortarType": "dvsn"},
            "중구": {"cortarNo": "1114000000", "centerLat": 37.563842, "centerLon": 126.9976, "cortarType": "dvsn"},
            "중랑구": {"cortarNo": "1126000000", "centerLat": 37.606324, "centerLon": 127.092584, "cortarType": "dvsn"},
        }         
            
        cortarList = []
        for gu in gu_result:
            guName = list(gu.keys())[0]
            if guName in gu_map:
                info = gu_map[guName].copy()
                info["cortarName"] = guName
                cortarList.append(info)

        return cortarList

    
    #구 번호로 동 cortarNo 가져오기
    def getcortarDong(self, cortarList, gu_result):
        result = []

        # gu_result 예: [{'강북구': '미아동,번동,우이동'}]
        # dict에서 구 이름과 동 리스트 추출
        for gu_dict in gu_result:
            guName = list(gu_dict.keys())[0]
            dong_names = gu_dict[guName].split(",")  # "미아동,번동,우이동" → ['미아동','번동','우이동']

            # cortarList에서 해당 구 정보 찾기
            for cortarInfo in cortarList:
                if cortarInfo['cortarName'] == guName:
                    cortarNo = cortarInfo['cortarNo']
                    url = f"https://new.land.naver.com/api/regions/list?cortarNo={cortarNo}"

                    json_data = self.getNaverApi(url)
                    dong_list = json_data.get("regionList", [])

                    # gu_result 동명과 일치하는 항목만 필터링
                    for d in dong_list:
                        if d['cortarName'] in dong_names:
                            result.append(d)
        if result:
            return result
        else:
            # 못 찾으면 기본값 반환
            return [{'cortarNo': '-1', 'abnomalData': dong_names}]

    
    #해당 동의 위치정보 가져오기
    def getLatLon(self, cortarDong):
        
        url = f"https://new.land.naver.com/api/cortars?zoom=16&centerLat={cortarDong['centerLat']}&centerLon={cortarDong['centerLon']}"
        json_data = self.getNaverApi(url) 

        return json_data.get("cortarVertexLists", [])[0]


    #위치정보 기반으로 최종 아파트 매물 리스트 가져오기
    def getAptList(self, aptCon, coords):     
        
        latitudes = [lat for lat, lon in coords]
        longitudes = [lon for lat, lon in coords]

        # 최댓값과 최솟값 계산
        min_lat = min(latitudes)
        max_lat = max(latitudes)
        min_lon = min(longitudes)
        max_lon = max(longitudes)

        # 결과 출력
        # print(f"최소 위도: {min_lat}")
        # print(f"최대 위도: {max_lat}")
        # print(f"최소 경도: {min_lon}")
        # print(f"최대 경도: {max_lon}")
        
        #최종 파라미터
        base_url = "https://new.land.naver.com/api/complexes/single-markers/2.0"
        # 파라미터 정의 (JSON 형태 + 설명 주석)
        params = {
            "cortarNo": aptCon['cortarNo'],              # 행정동 코드 (예: 서울 강남구 역삼동)
            "zoom": 16,                            # 지도 줌 레벨
            "priceType": "RETAIL",                 # 가격 타입: RETAIL = 일반매매
            "markerId": "",                        # 마커 ID (선택된 마커가 있을 경우 지정)
            "markerType": "",                      # 마커 타입 (ex: 단지, 건물 등)
            "selectedComplexNo": "",              # 선택된 단지 번호
            "selectedComplexBuildingNo": "",      # 선택된 건물 번호
            "fakeComplexMarker": "",              # 가상 단지 마커 여부
            "realEstateType": "APT",              # 부동산 유형: APT = 아파트
            "tradeType": "A1",                    # 거래 유형: A1 = 매매, B1 = 전세, B2 = 월세
            "tag": "::::::::",                    # 태그 필터 (URL 인코딩된 상태, 비워두면 필터 없음)
            "rentPriceMin": 0,                    # 최소 임대 가격
            "rentPriceMax": aptCon['priceMax'],          # 최대 임대 가격
            "priceMin": aptCon['priceMin'],                        # 최소 매매가 (단위: 만 원 → 5억 원)
            "priceMax": aptCon['priceMax'],                   # 최대 매매가 (단위: 만 원 → 12억 원)
            "areaMin": aptCon['areaMin'],                       # 최소 전용면적 (㎡)
            "areaMax": aptCon['areaMax'],                       # 최대 전용면적 (㎡)
            "oldBuildYears": aptCon['years'],                  # 오래된 건물 기준 필터 (미지정)
            "recentlyBuildYears": "",            # 최근 건축 연도 필터 (미지정)
            "minHouseHoldCount": "" ,            # 최소 세대 수
            "maxHouseHoldCount": "",             # 최대 세대 수 (미지정)
            "showArticle": "false",              # 매물 정보 표시 여부
            "sameAddressGroup": "false",         # 동일 주소 그룹 여부
            "minMaintenanceCost": "",            # 최소 관리비 (미지정)
            "maxMaintenanceCost": "",            # 최대 관리비 (미지정)
            "directions": "",                    # 방향 (동향, 남향 등 필터, 미지정)
            "leftLon": {min_lon},              # 지도 좌측 경도
            "rightLon": {max_lon},             # 지도 우측 경도
            "topLat": {max_lat},                # 지도 상단 위도
            "bottomLat": {min_lat},             # 지도 하단 위도
            "isPresale": "false"                 # 분양 여부: false는 기존 매물
        }
        
        query_string = urllib.parse.urlencode(params, doseq=True)
        final_url = f"{base_url}?{query_string}"

        json_data = self.getNaverApi(final_url)
    
        return json_data

    def getAptSaleInfo(self, complexNo):
        url = f"https://new.land.naver.com/api/complexes/overview/{complexNo}?complexNo={complexNo}&isClickedMarker=true"
        
        json_data = self.getNaverApi(url)
        return json_data


mainService = MainService()