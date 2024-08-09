import requests  # 导入requests库，用于发送HTTP请求
import base64  # 导入base64库，用于进行编码

# FOFA API的配置信息
API_URL = "https://fofa.info/api/v1/search/all"  # FOFA搜索接口URL
API_KEY = "849489858@qq.com"  # 假设的API密钥
SECRET = "30bffdb13deccd433f6505f2dc699972"  # 假设的密文

# 搜索参数
QUERY = ""udpxy" && country="CN" && region="Henan""  # 用户自定义的查询语句，例如: "protocol=\"http\""
PAGE = 1  # 请求的页码
PAGE_SIZE = 50  # 每页条数，最大100

def get_token(key, secret):
    """
    获取访问令牌的函数
    :param key: API密钥
    :param secret: 与API密钥对应的密文
    :return: 访问令牌
    """
    url = "https://fofa.info/api/v1/info/ip"  # 获取Token的API接口URL
    data = {
        "email": key,  # 传入API密钥
        "key": secret  # 传入密文
    }
    response = requests.post(url, json=data)  # 发送POST请求获取Token
    return response.json().get("data", {}).get("Token")  # 安全地获取Token

def search_fofa(query, page, page_size, token):
    """
    使用FOFA进行搜索的函数
    :param query: 搜索查询语句
    :param page: 当前页码
    :param page_size: 每页条数
    :param token: 访问令牌
    :return: 搜索结果
    """
    url = API_URL  # 使用FOFA的搜索接口URL
    data = {
        "email": API_KEY,  # 传入API密钥
        "key": SECRET,  # 传入密文
        "qbase64": base64.b64encode(query.encode('utf-8')).decode('utf-8'),  # 对查询语句进行Base64编码
        "page": page,  # 页码
        "size": page_size,  # 每页条数
        "token": token  # 访问令牌
    }
    headers = {
        "Range": f"items={page}-{page*page_size}"  # 设置请求头，指定请求的数据范围
    }
    response = requests.post(url, data=data, headers=headers)  # 发送POST请求进行搜索
    return response.json()  # 返回从响应中解析出的JSON数据

if __name__ == "__main__":
    token = get_token(API_KEY, SECRET)  # 调用get_token函数获取Token
    if token:  # 确保获取到有效的Token
        results = search_fofa(QUERY, PAGE, PAGE_SIZE, token)  # 调用search_fofa函数进行搜索
        # 处理结果
        if "error" in results and results["error"]:  # 检查是否有错误信息
            print(results["errmsg"])  # 打印错误信息
        else:
            for result in results.get("data", []):  # 安全地获取数据
                print(result)  # 打印每个结果
    else:
        print("获取Token失败，请检查API_KEY和SECRET是否正确。")  # 如果Token获取失败，打印提示信息
