

def GeoCoordinates(addr):
    import os
    import sys
    import urllib.request

    client_id = "ZbNWupFQAk_cmBAmLstr"
    client_secret = "5_knjXBU5Z"

    encText = urllib.parse.quote(addr)
    url = "https://openapi.naver.com/v1/map/geocode?query=" + encText # json 결과
    # url = "https://openapi.naver.com/v1/map/geocode.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        mystr = response_body.decode('utf-8')
        mystr = mystr.replace('true',"True")
        mystr = mystr.replace('false',"False")
        mydic = eval(mystr)
    else:
        print("Error Code:" + rescode)
    return mydic