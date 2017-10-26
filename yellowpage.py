import os
import sys
import my_mongodb
from bs4 import BeautifulSoup
import multiprocessing as mp
import requests
import time

sys.setrecursionlimit(1000000)


def get_source(my_url, time_out=15):
    """获取url的源代码,返回页面源代码"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.1.1.1000 Chrome/55.0.2883.75 Safari/537.36"}
    r = requests.get(my_url, headers=headers, timeout=time_out)
    if r.status_code == 200:
        return r.content.decode()
    else:
        return 1


def read_html(data_file):
    soup = BeautifulSoup(data_file, 'lxml')
    text = soup.find('ul', class_='txl_content_con_L')
    title = text.find('h1').string.strip()
    li_pool = text.find_all('li')
    region = None
    try:
        if li_pool[0].contents[1].string and li_pool[0].contents[3].string:
            region = li_pool[0].contents[1].string + ' ' + li_pool[0].contents[3].string
        elif text.find('a').contents:
            region = text.find('a').contents[0]
    except IndexError:
        region = None
    contact = text.contents[5].string.strip()[4:].replace('\r', '').replace('\n', '').replace('\t', '')
    fax = text.contents[7].string.strip()[3:]
    telephone = text.contents[9].string.strip()[8:]
    mobilephone = text.contents[11].string.strip()[5:]
    address = text.contents[13].string.strip()[5:]
    data = dict(地区=region, 名称=title, 联系人=contact, 传真=fax, 电话=telephone, 手机=mobilephone, 地址=address)
    return data


def write_log(str_log):
    str_time2s = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
    f = open('out.log', 'a')
    f.write(str_time2s + " :" + str_log + '\n')
    f.close()


def get_data(start, end):
    pool = mp.Pool(processes=4)
    if start >> end:
        return 1
    for i in range(start, end):
        try:
            my_url = "http://book.youboy.com/com/" + str(i) + ".html"
            print(my_url)
            source = pool.apply_async(get_source, args=(my_url,)).get()
            if source != 1:
                a = read_html(source)
                a['uid'] = i
                x = my_mongodb.my_mongodb_se()
                x.my_mongo_client["com_contact"]["1"].insert_one(a)
                print("ok!")
        except Exception as error:
            write_log("error:"+str(i)+"  "+str(error))
            continue


if __name__ == '__main__':
    get_data(823444, 1500000)
    os.system("shutdown -s -t 60")
