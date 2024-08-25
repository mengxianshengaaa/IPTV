import requests
# 定义txt文件的URL列表
urls = [
    'https://raw.githubusercontent.com/kimwang1978/tvbox/main/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83/lives/%E2%91%AD%E5%BC%80%E5%BF%83%E7%BA%BF%E8%B7%AF.txt',#################
    'https://raw.githubusercontent.com/pxiptv/live/main/iptv.txt', #ADD 【2024-08-02 16:48:40】#每日更新1次
    'https://notabug.org/vnjd/yydu/raw/master/yyfug.txt', #ADD 【2024-08-06】
    'https://tvkj.top/tvlive.txt', #ADD 【2024-08-06】
    'https://pan.beecld.com/f/OXMcA/%E6%98%A5%E8%B5%A2%E5%A4%A9%E4%B8%8B.txt', #ADD 【2024-08-06】
    'http://kxrj.site:55/lib/kx2024.txt',   #ADD 【2024-08-07】
    'https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt',   #ADD 2024-08-05 每天更新一次，量太多转到blacklist处理
    'https://wzsvip.github.io/ipv4.txt',   #ADD 【2024-08-08】
    'http://wz.42web.io/ipv4.txt',   #ADD 【2024-08-08】
    'http://ttkx.live:55/lib/kx2024.txt',   #ADD 【2024-08-10】每日更新3次，移动到main.py
    'http://mywlkj.ddns.net:5212/f/EErCL/%E5%8F%B0%E6%B9%BE%E7%94%B5%E8%A7%86TV.txt',   #ADD 【2024-08-10】
    'https://raw.githubusercontent.com/Guovin/TV/gd/result.txt', #每天自动更新1次
    'https://raw.githubusercontent.com/ssili126/tv/main/itvlist.txt', #每天自动更新1次
    'https://raw.githubusercontent.com/mlvjfchen/TV/main/iptv_list.txt', #每天早晚各自动更新1次 2024-06-03 17:50
    'https://raw.githubusercontent.com/fenxp/iptv/main/live/ipv6.txt',  #1小时自动更新1次11:11 2024/05/13
    'https://raw.githubusercontent.com/fenxp/iptv/main/live/tvlive.txt', #1小时自动更新1次11:11 2024/05/13
    'https://raw.githubusercontent.com/zwc456baby/iptv_alive/master/live.txt',  #每天自动更新1次 2024-06-24 16:37
    'http://ttkx.live:55/lib/kx2024.txt', #ADD 2024-08-11 每天更新3次
    'https://raw.githubusercontent.com/vbskycn/iptv/master/tv/iptv4.txt', #ADD 2024-08-12 每天更新3次
]
# 合并文件的函数
def merge_txt_files(urls, output_filename='汇总.txt'):
    try:
        # 打开文件准备写入
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for url in urls:
                try:
                    # 发送HTTP GET请求
                    response = requests.get(url)
                    # 检查请求是否成功
                    response.raise_for_status()
                    # 读取内容并写入输出文件
                    outfile.write(response.text + '\n')
                except requests.RequestException as e:
                    # 打印错误信息并继续下一个循环
                    print(f'Error downloading {url}: {e}')
    except IOError as e:
        # 处理文件写入错误
        print(f'Error writing to file: {e}')
# 调用函数
merge_txt_files(urls)
