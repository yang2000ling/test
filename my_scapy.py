import requests
import time,sys


def sleep(sleep_time):
    """延时函数（单位：秒）"""
    time.sleep(sleep_time)
    print('sleep:' + str(sleep_time) + 's')


def get_source(url, my_data=None, is_ios_header=0, time_out=15):
    """获取url的源代码,返回页面源代码"""
    header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8",
        "Accept - Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    ios_header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"}
    if is_ios_header == 0:
        my_header = header
    else:
        my_header = ios_header
    #print('get_source:',url,'\nparams:',my_data)
    r = requests.get(url, headers=my_header, params=my_data, timeout=time_out, )
    return r

def write_log(str_log, file_name='out_log.txt'):
    """str_log写入信息,file_name为日志文件名"""
    str_time2s = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
    f = open(file_name, 'a')
    f.write(str_time2s + " :" + str(str_log) + '\n')
    f.close()

def pro_gressbar(str_data,now_num,end_num):
    sys.stdout.write('\r')
    sys.stdout.write(str_data+str(now_num)+'/'+str(end_num))
    sys.stdout.flush()  ##随时刷新到屏幕上
    time.sleep(0.1)
