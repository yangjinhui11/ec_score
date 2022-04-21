# -*- coding: utf-8 -*-
"""
Spyder 杨锦辉 20220420

通过发送请求爬取ECMWF统计检验数据.
使用是需要修改日期
"""
import numpy as np
import requests
import csv
import json
import pandas as pd
import os
#模拟浏览器环境头
headers = {
    "access-control-allow-credentials": "true",
"access-control-allow-origin": "https://apps.ecmwf.int",
"access-control-expose-headers": "Set-Cookie, User-Auth",
#"date": "Tue, 19 Apr 2022 07:38:45 GMT",
"strict-transport-security": "max-age=15552000",
"vary": "Cookie, Origin",
"authority": "apps.ecmwf.int",

"origin": "https://apps.ecmwf.int",
"referer": "https://apps.ecmwf.int/wmolcdnv/scores/mean/850_t",

"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44",
"x-requested-with": "XMLHttpRequest"
    }
addr = "https://apps.ecmwf.int/wmolcdnv/get-probe/mean/{0}/"
datas = {"select":
     {"param_level":"700_r","domain_name":"n.hem","running_mean_window":1,
      "score":"rmsef","date":202203,"vstream":"wmo2_an","type":"mean"},
     "plot_list":{"ammc_00":1,"ammc_12":1,"ecmf_00":1,"ecmf_12":1,"edzw_00":1,"edzw_12":1,"egrr_00":1,"egrr_12":1,"kwbc_00":1,"kwbc_12":1,"lfpw_00":1,"lfpw_12":1,"rjtd_00":1,"rjtd_12":1,"rksl_00":1,"rksl_12":1},
     "coordinates":{"x":167.88484552556818,"y":29.2449824359258}}
Fields=[
        #"msl", #mean sea level pressure
        "850_z",# 850 hPa Geopotential
        "850_t",# 850 hPa Temperature
        #"850_ff",# 850 wind
        "700_r", # 700 hPa Humidity
        "500_z", # 500 hPa Geopotential
        "500_t", # 500 hPa Temperature
#        "500_ff", # 500 wind
        "250_z" , # 250 hPa Geopotential
        "250_t" , # 250 hPa Temperature
#        "250_ff", # 250 hPa wind
        ]
scores=["ccaf", # anomaly correlation
        "rmsef" # rmse 
        ]
domains=["n.hem",
        "s.hem",
        "tropics",
        "asia",
        #"europe",
        #"n.amer",
        "s.pole",
        "n.pole"
        ]
years=[2012+i for i in range(9)]
#years=[2022]
months=[i+1 for i in range(12)]
dates=["{0}{1:0>2d}".format(year,mon)  for year in years for mon in months]




def get_240hour_score(url,datas):
    
    hour_dic=[]
    for x in range(10):
        hours=(x+1)*24
        print("hours={0}".format(hours))
        datas["coordinates"]["x"] = hours
        res=requests.post(url,headers=headers,json=datas)
        vobj = json.loads(res.text)
        values = vobj["values"]
        df1 = pd.DataFrame(values)
        df1.rename(columns={"value":hours},inplace=True)
        try:
            df1 = df1.set_index("caption")
        except Exception as e:
            print(e)
            print(res.text)
            return []
        hour_dic.append(df1)
    if(len(hour_dic)>0):
        tenday=pd.concat(hour_dic,axis=1)
    return tenday

def get_years_score(url,dates,datas):
    
    fname = "./mean/{0}_{1}_{2}_{3}_{4}.xls".format(dates[0],dates[-1],datas["select"]["domain_name"],datas["select"]["param_level"],datas["select"]["score"])
    print(fname)
    if os.path.exists(fname):
        print(fname+" file exists!")
        return 
    date_list=[]
    for date in dates:
        datas["select"]["date"] = date
        print(datas["select"])
        tenday_df = get_240hour_score(url,datas)
        if(len(tenday_df)==0):
            return
        date_list.append(tenday_df)
    if(len(date_list)==0):
        return
    writer = pd.ExcelWriter(fname)
    date_df=pd.concat(date_list,keys=dates)
    print(date_df)
    date_df.to_excel(writer)
    writer.save()
    writer.close()
    print("write fiel "+fname)
    
for field in Fields:
    url = addr.format(field)
    datas["select"]["param_level"]=field
    for score in scores:
        datas["select"]["score"] = score
        
        for dom in domains:
            
            datas["select"]["domain_name"] = dom
            get_years_score(url,dates,datas)
    
        
