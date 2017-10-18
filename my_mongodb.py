import pandas
from pymongo import MongoClient
import json
import csv


def txt2list(txt_path):
    """读取txt文件，转换成list"""
    data_dict = []
    with open(txt_path, 'r') as txtFile:
        s = txtFile.readlines()
        for i in s:
            i = i[:-1]
            data_dict.append(i)
    return data_dict


def csv2df(file_path):
    """读取txt文件，转换成DataFrame类型"""
    data = []
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    df = pandas.DataFrame(data[1:], columns=data[0])
    return df


class my_mongodb_se:
    def __init__(self, hostname='127.0.0.1', db_port=27017):
        """初始化类，初始化数据库连接"""
        self.hostname = hostname
        self.db_port = db_port
        self.my_mongo_client = MongoClient(self.hostname, self.db_port)

    def df2mongodb(self, df_data, db_name, form_name):
        """DataFrame数据写入mongodb"""

        def df2bson(df):
            """DataFrame类型转化为Bson类型"""
            data = json.loads(df.T.to_json()).values()
            return data

        my_db = self.my_mongo_client[db_name]
        bson_data = df2bson(df_data)
        my_posts = my_db[form_name]
        result = my_posts.insert_many(bson_data)
        return result

    def collection2df(self, db_name, collection_name, query={}, no_id=True):
        """查询数据库，导出DataFrame类型数据
        （db_name：数据库名 collection_name：集合名 query：查询条件式 no_id：不显示ID,默认为不显示ID）"""
        db = self.my_mongo_client[db_name]
        collection = self.my_mongo_client[db_name][collection_name]
        cursor = collection.find(query)
        df = pandas.DataFrame(list(cursor))
        if no_id:
            del df['_id']
        return df

    def csv2mongodb(self, csv_path, db_name, collection_name):
        """CSV文件写入mongodb"""
        df = csv2df(csv_path)
        result = self.df2mongodb(df, db_name, collection_name)
        return result


'''if __name__ == '__main__':
    a = my_mongodb_se()
    a.csv2mongodb("f:/鸽药商品.csv", "test_db", "csv_test")'''
