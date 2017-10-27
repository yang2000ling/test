import requests
from bs4 import BeautifulSoup
import pymongo
import multiprocessing as mp
import time

def get_source(my_url, time_out=15):
    """获取url的源代码,返回页面源代码"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.1.1.1000 Chrome/55.0.2883.75 Safari/537.36"}
    r = requests.get(my_url, headers=headers, timeout=time_out)
    if r.status_code == 200:
        return r.content.decode(r.encoding)
    else:
        return 1

def read_html(data_file):
    soup = BeautifulSoup(data_file, 'lxml')
    text = soup.find('div',class_= 'NewsContent')
    data = text.find_all('p')
    com_info={}
    for i in range(0, len(data)-1, 2):
        key = data[i].string.strip().replace('\xA0','')
        value = data[i+1].string.strip().replace('\xA0','')
        com_info[key]=value
    return com_info

def write_log(str_log):
    str_time2s = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
    f = open('ubaike_out.log', 'a')
    f.write(str_time2s + " :" + str_log + '\n')
    f.close()

def insert_data(data, db_name, collection_name, hostname='127.0.0.1',db_port=27017):
    my_mongo_client = pymongo.MongoClient(hostname, db_port)
    if my_mongo_client[db_name][collection_name].find({'uid':data['uid']}).count()!=0:
        print('update:',data['uid'])
        r=my_mongo_client[db_name][collection_name].update({'uid':data['uid']},data)
    else:
        print('insert:',data['uid'])
        r=my_mongo_client[db_name][collection_name].insert_one(data)
    return r

def get_data(start, end, db_name , collection_name):
    pool = mp.Pool(processes=2)
    if start >> end:
        return 1
    for i in range(start, end):
        try:
            my_url = "http://www.ubaike.cn/show_" + str(i) + ".html"
            print(my_url)
            source = pool.apply_async(get_source, args=(my_url,)).get()
            if source != 1:
                a = read_html(source)
                a['uid'] = i
                insert_data(a,db_name,collection_name)
                print("ok!")
        except Exception as error:
            write_log("error:"+str(i)+"  "+str(error))
            continue


if __name__ == '__main__':
    get_data(1,100,'www_ubaike_cn','test')
