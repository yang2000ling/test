import requests
from bs4 import BeautifulSoup
import time


def sleep(sleep_time):
    """延时函数（单位：秒）"""
    time.sleep(sleep_time)
    print('sleep:' + str(sleep_time) + 's')


def get_source(url, my_data, is_ios_header=0, time_out=15):
    """获取url的源代码,返回页面源代码"""
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.1.1.1000 Chrome/55.0.2883.75 Safari/537.36"}
    ios_header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"}
    if is_ios_header == 0:
        my_header = header
    else:
        my_header = ios_header
    r = requests.get(url, headers=my_header, params=my_data, timeout=time_out, )
    return r