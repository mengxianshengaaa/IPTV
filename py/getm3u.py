from bs4 import BeautifulSoup
import requests
import sys
import time

def parse_list():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://tonkiang.us/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    r = requests.get('http://tonkiang.us/', headers=headers, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    parse_result = {}
    for box in soup.select('div.box'):
        box_name = box.find('div').string.strip()
        items = [x.string for x in box.select('span > a')]
        parse_result[box_name] = items
    print(f'打印parse_result：{parse_result}')
    return parse_result

def search_ip(ip: str):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
       'Referer': 'http://tonkiang.us/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    params = {
        's': ip,
    }
    r = requests.get('http://tonkiang.us/hoteliptv.php', params=params, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    group_name = []
    group_ip = []
    for a in soup.select('div > i'):
        g_name = a.string.strip()
        if '组播' in g_name:
            index = g_name.index('上线') + 2
        if '酒店' in g_name:
            index = g_name.index('上线') + 2
        g_namestring = g_name[index:]
        group_name.append(g_namestring.strip())
    for b in soup.select('div.channel > a > b'):
        b.img.extract()
        group_ip.append(b.string.strip())
    return group_name,group_ip

def parse(address: str):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://tonkiang.us/hotellist.html?s=223.10.16.11:8085',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    r = requests.get(f'http://tonkiang.us/alllist.php?s={address}&c=false', headers=headers, verify=False)
    parse_result = []
    soup = BeautifulSoup(r.text, 'html.parser')
    for result in soup.select('div.result'):
        name_div = result.find('div', style="float: left;")
        m3u8_div = result.find('td', style="padding-left: 6px;")
        if name_div and m3u8_div:
            parse_result.append({
                "name": name_div.string,
                "m3u": m3u8_div.string.strip()
            })
    # print(f'打印parse_result:{parse_result}')
    return parse_result

def gen_m3u(group):
    with open(sys.path[0] + "\\public\\iptv.m3u", "w+", encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'#EXT-X-VERSION {int(time.time())}\n')
        f.write('\n')
        index = 1
        for (group_name, parse_result) in group.items():
            for one in parse_result:
                f.write(f'''#EXTINF:-1,tvg-id="{index}-{one['name']}" tvg-name="{index}-{one['name']}" group-title="{group_name}",{one['name']}\n''')
                f.write(one['m3u'])
                f.write('\n')
            index = index + 1

    print("m3u生成成功！")


if __name__ == "__main__":
    result = {}
    ps = []
    ps_name = []
    parse_list = parse_list()
    for (group_name, items) in parse_list.items():
        if group_name == 'Multicast IP':
            for ip in items:
               mu_name,mu_ip = search_ip(ip)
               ps.extend(mu_ip)
               ps_name.extend(mu_name)
    for (group_name, items) in parse_list.items():
        if group_name == 'Hotel IPTV':
            for ip in items:
                hot_name, hot_ip = search_ip(ip)
                ps.extend(hot_ip)
                ps_name.extend(hot_name)
    # print(f'ps：{ps}')
    print(f'ps_name：{ps_name},{len(ps_name)}')
    for x in [x for x in ps if x is not None]:
        try:
            rs = parse(x)
            for y in [y for y in ps_name if y is not None]:
                result[y] = rs
                # print(f'打印result:{result}')
        except Exception as e:
            print(e)
    gen_m3u(result)