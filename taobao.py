import requests
from bs4 import BeautifulSoup
import re
import json
import time
import pandas as pd
import multiprocessing as mp
import my_scapy


def get_pro_detail(pro_id):
    """获取商品具体数据"""
    pro_detail={}
    params_data = '{"exParams":"{\"id\":\"'+str(pro_id)+'\"}","itemNumId":"'+str(pro_id)+'"}'
    my_data = dict(appKey='12574478', t='1508764187310', sign='0629bfbee38e1d8cec9e25b4cb9afae6',
                   api='mtop.taobao.detail.getdetail', v='6.0', ttid='2016 @ taobao_h5_2.0.0', isSec='0', ecode='0',
                   AntiFlood='true', AntiCreep='true', H5Request='true', type='jsonp', dataType='jsonp',
                   callback='mtopjsonp1',
                   data=params_data)
    url = "https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/"
    source = my_scapy.get_source(url, my_data, is_ios_header=1)
    page_data = source.content.decode()
    # print(page_data)
    if re.findall(r'"sellCount\\":\\"(.+?)\\"', page_data):
        month_count = re.findall(r'"sellCount\\":\\"(.+?)\\"', page_data)
        pro_detail['月销量'] = month_count[0]
    if re.findall(r'"subtitle":"(.+?)"',page_data):
        subtitle = re.findall(r'"subtitle":"(.+?)"',page_data)
        pro_detail['商品描述'] = subtitle[0]
    if re.findall(r'"favcount":"(.+?)"',page_data):
        favcount = re.findall(r'"favcount":"(.+?)"',page_data)
        pro_detail['收藏数'] = favcount[0]
    if re.findall(r'{"基本信息.*?}]}', page_data):
        pro_info = re.findall(r'{"基本信息.*?}]}', page_data)[0]
        pro_info = json.loads(pro_info)
        pro_detail['基本信息'] = str(pro_info["基本信息"])
    return pro_detail


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
        source = my_scapy.get_source(url).content.decode()
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
            data.append((pool.apply_async(my_scapy.get_source, args=(url,))).get().content.decode())
        pool.close()
        pool.join()
        keyword_data = self.get_pageinfo(data, flag)
        df = pd.DataFrame(keyword_data)
        df["rank"] = df.index
        df["date"] = self.str_time
        return df


# ------------------------------------------------
if __name__ == '__main__':
    #start = time.clock()
    #a = get_pro_detail(548056260209)
    #print(a)
    x = TaoBaoKeyword('三连冠鸽药')
    df1 = x.get_info('pro')
    a = list(df1['nid'])
    for i in a:
       print(get_pro_detail(i))
    #end = time.clock()
    #print(end - start)
