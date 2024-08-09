import requests  # 导入requests库，用于发送HTTP请求
import base64  # 导入base64库，用于进行编码

# FOFA API的配置信息
API_URL = "https://fofa.info/api/v1/search/all"  # FOFA搜索接口URL
API_KEY = "849489858@qq.com"  # 假设的API密钥
SECRET = "30bffdb13deccd433f6505f2dc699972"  # 假设的密文

PAGE = 1
PAGE_SIZE = 50  # 每页条数，fofa API 限制最大 100
 
def get_token(key, secret):
    url = "https://fofa.info/api/v1/info/ip"
    data = {
        "email": key,
        "key": secret
    }
    response = requests.post(url, data=data)
    return response.json()["data"]["Token"]
 
def search_fofa(query, page, page_size, token):
    url = API_URL
    data = {
        "email": API_KEY,
        "key": SECRET,
        "qbase64": base64.b64encode(query.encode('utf-8')).decode('utf-8'),
        "page": page,
        "size": page_size,
        "token": token
    }
    headers = {
        "Range": f"items {page}-{page_size}"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()
 
if __name__ == "__main__":
    token = get_token(API_KEY, SECRET)
    results = search_fofa(QUERY, PAGE, PAGE_SIZE, token)
    # 处理结果
    for result in results:
        print(result)
        for result in results.get("data", []):  # 安全地获取数据
           print(result)  # 打印每个结果
    else:
        print("获取Token失败，请检查API_KEY和SECRET是否正确。")  # 如果Token获取失败，打印提示信息
