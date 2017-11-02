import my_scapy
from bs4 import BeautifulSoup
import pandas
import my_mongodb
import multiprocessing as mp
import sys

sys.setrecursionlimit(1000000)


def read_list_html(url):
    source = my_scapy.get_source(url, is_ios_header=1).content.decode()
    soup = BeautifulSoup(source, 'lxml')
    text = soup.find('ul', class_='jl_list')
    href = text.find_all('a')
    data_list = []
    pool = mp.Pool(processes=2)
    for i in href:
        try:
            p_url = 'http://m.qzrc.com' + i.get('href')
            # data=read_p_html(p_url)
            data = pool.apply_async(read_p_html, args=(p_url,)).get()
            data_list.append(data)
        except Exception as error:
            my_scapy.write_log("error:" + str(i) + "  " + str(error))
            continue
    pool.close()
    pool.join()
    return data_list


def read_p_html(p_url):
    p = my_scapy.get_source(p_url, is_ios_header=1)
    data_list = {}
    if p.status_code == 200:
        source = p.content.decode()
        # print(source)
        soup = BeautifulSoup(source, 'lxml')
        note_more = soup.find('div', 'note_more').string
        data_list['个人简历'] = note_more
        p_li = soup.find('ul', 'list list_float')
        p_li = p_li.find_all('li')
        data_list['联系信息'] = p_li[0].string[5:]
        data_list['联系电话'] = p_li[1].string[5:]
        data_list['电子邮箱'] = p_li[2].string[5:]
        data_list['QQ'] = p_li[3].string[3:]
        data_list['地址'] = p_li[4].string[5:]
        p = soup.find_all('ul', 'list')
        p_p = p[0].find_all('li')
        data_list['姓名'] = p_p[0].string[3:]
        data_list['性别'] = p_p[1].string[3:]
        data_list['体重'] = p_p[2].string[3:]
        data_list['身高'] = p_p[3].string[3:]
        data_list['学历'] = p_p[4].string[3:]
        data_list['工作经历'] = p_p[5].string[5:]
        data_list['毕业时间'] = p_p[6].string[5:]
        p_p2 = p[1].find_all('li')
        data_list['工作类型'] = p_p2[0].string[6:]
        data_list['行业类别'] = p_p2[1].string[6:]
        data_list['工作地点'] = p_p2[2].string[6:]
        data_list['月薪范围'] = p_p2[3].string[6:]
        data_list['刷新日期'] = p_p2[4].string[6:]
        data_list['职位类别'] = p_p2[6].string[6:]
        data_list['所学专业'] = p_p2[7].string[6:]
        data_list['求职岗位'] = p_p2[8].string[6:]
    return data_list


def get_data(start, end):
    if start >> end:
        return 1
    for i in range(start, end):
        try:
            my_url = "http://m.qzrc.com/PersonList.html?pageindex=" + str(i)
            data = read_list_html(my_url)
            df = pandas.DataFrame(data)
            x = my_mongodb.my_mongodb_se()
            x.df2mongodb(df, 'm_qzrc_com', '1')
            my_scapy.write_log(my_url + "     ok!")
            print("ok!")
        except Exception as error:
            my_scapy.write_log("error:" + str(i) + "  " + str(error))
            continue


if __name__ == '__main__':
    get_data(1, 80)
