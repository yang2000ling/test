import my_mongodb

x=my_mongodb.my_mongodb_se()
a=x.collection2df('m_qzrc_com','1',{'联系电话':{'$regex':"^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\\d{8}$"}})
a.to_csv('f:/qzrc.csv')