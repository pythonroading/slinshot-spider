import os
import json
import requests
import time
import random
from bs4 import BeautifulSoup

url_base = "https://www.bhhzw.com/"
uapool = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"
]
headers = {
    "Referer": url_base,
    'User-Agent': random.choice(uapool)
}


jsonfile = "D:/PycharmProjectsuntitled/webCrawler/baihehua_img/json"
dirs = os.listdir(jsonfile)



for i in dirs:
    with open(jsonfile + '/' + i, "r", encoding='utf-8') as f:
        data = json.load(f)
    # 一层级文件夹
    filet = data['title']
    va1 = os.getcwd() + '/' + filet
    isExists = os.path.exists(va1)
    # 创建目录
    if not isExists:
        os.makedirs(va1)
    # 妹子单独
    meizilist = data['g']
    # 路径转义
    print(len(meizilist))
    for i in meizilist:
        print(i['filename'])
        filename = i['filename'].replace(' ', '')
        meizidir = va1 + '/' + filename
        # 创建妹子文件夹
        if not os.path.exists(meizidir):
            os.makedirs(meizidir)
        meizihref = i['href']
        time.sleep(3)
        text = requests.get(meizihref, headers=headers, timeout=5).text
        soup = BeautifulSoup(text, 'lxml')
        img = soup.select('#masonry div img')
        imgs = []
        for data in img:
            imgs.append(data['data-original'])
        i = 1
        for url_img in imgs:
            # 请求图片资源
            # time.sleep(2)
            imgsource = requests.get(url_img, headers=headers)
            file_name = str(i) + '.jpg'
            path = meizidir  +'/'+ file_name
            print(path)
            try:
                with open(path, 'wb') as f:
                    f.write(imgsource.content)
                    print("\t|" + file_name + '\tSuccessful')
            except Exception as E:
                print(E)
            i += 1;
        exit(0)

