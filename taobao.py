import requests
from bs4 import BeautifulSoup
import re
import json
import time
import pandas as pd
import multiprocessing as mp


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


def get_pro_detail(pro_id):
    """获取商品具体数据"""
    params_data = '{"exParams":"{\"id\":\"'+str(pro_id)+'\"}","itemNumId":"'+str(pro_id)+'"}'
    my_data = dict(appKey='12574478', t='1508764187310', sign='0629bfbee38e1d8cec9e25b4cb9afae6',
                   api='mtop.taobao.detail.getdetail', v='6.0', ttid='2016 @ taobao_h5_2.0.0', isSec='0', ecode='0',
                   AntiFlood='true', AntiCreep='true', H5Request='true', type='jsonp', dataType='jsonp',
                   callback='mtopjsonp1',
                   data=params_data)
    url = "https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/"
    source = get_source(url, my_data, is_ios_header=1)
    page_data = source.content.decode()
    print(page_data)
    month_count = re.findall(r'"sellCount\\":\\"(.+?)\\"', page_data)
    print('month_count=', month_count)
    pro_info = re.findall(r'{"基本信息.*?}]}', page_data)[0]
    pro_info = json.loads(str(pro_info))
    print(pro_info)


class TaoBaoKeyword:
    # 初始化类，key_word为关键词 默认2进程运行
    def __init__(self, key_word, process_num=2):
        self.key_word = key_word
        self.shop_counter_url = 'https://shopsearch.taobao.com/search?app=shopsearch&q=' + str(key_word)
        self.pro_counter_url = 'https://s.taobao.com/search?q=' + str(key_word) + '&sort=sale-desc&s=0'
        self.str_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.str_time2s = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
        self.process_num = process_num

    @staticmethod
    def page_counter(url):
        """获取页面计数"""
        source = get_source(url)
        soup = BeautifulSoup(source, 'lxml')
        page_num = re.findall(
            r'"pageSize":[^,]*,'
            r'"totalPage":[^,]*,'
            r'"currentPage":[^,]*,"'
            r'totalCount":[^}]*',
            str(soup))
        page_num = '{' + page_num[0] + '}'
        page_count_json = json.loads(page_num)
        return page_count_json['pageSize'], page_count_json['totalPage'], \
               page_count_json['currentPage'], page_count_json['totalCount']

    def keyword_counter(self):
        """获取关键词相关计数"""
        shop_counter = self.page_counter(self.shop_counter_url)
        pro_counter = self.page_counter(self.pro_counter_url)
        keyword_counter = {"关键词": self.key_word,
                           "单页店铺数量": shop_counter[0],
                           "店铺页面总数": shop_counter[1],
                           "店铺总数": shop_counter[3],
                           "单页商品数量": pro_counter[0],
                           "商品页面总数": pro_counter[1],
                           "商品总数": pro_counter[3]}
        df_counter = pd.DataFrame(data=keyword_counter, index=[0], columns=["关键词", "单页店铺数量",
                                                                            "店铺页面总数", "店铺总数",
                                                                            "单页商品数量", "商品页面总数",
                                                                            "商品总数"])
        df_counter["date"] = self.str_time
        return df_counter

    @staticmethod
    def get_pageinfo(page_sources, flag):
        """ 分析页面集合数据信息,flag="shop"或者flag="pro" """
        my_data = []
        for i in page_sources:
            soup = BeautifulSoup(i, 'lxml')
            if flag == 'shop':
                page_info = re.findall(r'"uid":"[^"]*",.*?"isTmall":[^,]*', str(soup))
            elif flag == 'pro':
                page_info = re.findall(r'"nid":"[^"]*",.*?"nick":"[^"]*"', str(soup))
            else:
                return False
            for n in range(len(page_info)):
                page_info[n] = '{' + page_info[n] + '}'
                json_data = json.loads(page_info[n])
                if flag == 'pro':
                    json_data["title"] = json_data["title"].replace('<span class=H>', '')
                    json_data["title"] = json_data["title"].replace('</span>', '')
                my_data.append(json_data)
        return my_data

    def get_info(self, flag):
        """ 获取关键词店铺商品DataFrame类型数据，flag="shop"或者flag="pro" """
        if flag == 'shop':
            my_counter = self.page_counter(self.shop_counter_url)
            my_url = 'https://shopsearch.taobao.com/search?app=shopsearch&q=' + self.key_word + '&sort=default&s='
        elif flag == 'pro':
            my_counter = self.page_counter(self.pro_counter_url)
            my_url = 'https://s.taobao.com/search?q=' + str(self.key_word) + '&sort=sale-desc' + '&s='
        else:
            return False
        pool = mp.Pool(processes=self.process_num)
        data = []
        for i in range(my_counter[1]):
            n = i * my_counter[0]
            url = my_url + str(n)
            data.append((pool.apply_async(get_source, args=(url,))).get())
        pool.close()
        pool.join()
        shop_data = self.get_pageinfo(data, flag)
        df = pd.DataFrame(shop_data)
        df["rank"] = df.index
        df["date"] = self.str_time
        return df


# ------------------------------------------------
if __name__ == '__main__':
    start = time.clock()
    get_pro_detail(539731830137)
    end = time.clock()
    print(end - start)
