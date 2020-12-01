import requests
import time
import random
import json
import os
from bs4 import BeautifulSoup


if __name__ == '__main__':

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
    text = requests.get(url_base, headers=headers).text
    soup = BeautifulSoup(text, 'lxml')
    ul = soup.select(".nav")[0]
    list = []
    for i in ul.find_all('li'):
        data = {
            "title": i.string,
            "href": i.a['href']
        }
        list.append(data)
    # 去获取各个栏目的页数
    for var1 in list:
        html = requests.get(var1['href'], headers=headers).text
        soup = BeautifulSoup(html, 'lxml').select(".page-navigator")[0]
        page = soup.find_all("li")[-2]
        # 获取每一个栏目的总页数
        var1['pages'] = 30 if int(page.string) > 50 else int(page.string)
    ##--------------------对方网站响应慢——------慢请求
    for i in list:
        base = i["href"]
        authors = []
        for index in range(1, i["pages"]+1):
            base_url = base + str(index)
            time.sleep(5)
            text = requests.get(base_url, headers=headers, timeout=10).text
            soup = BeautifulSoup(text, 'lxml')
            page = soup.select(".item-link")
            for p in page:
                author = {}
                filename = p.div.string
                href = p['href']
                author['filename'] = filename.replace("\n", "")
                author['href'] = href
                print(filename, href)

                authors.append(author)

        i['count'] = len(authors)
        i['g'] = authors

        # 写入json
        dir = os.getcwd()
        jsonfile = dir + '/json'
        isExists = os.path.exists(jsonfile)
        # 创建目录
        if not isExists:
            os.makedirs(jsonfile)
        file = jsonfile + i['title']+".json"
        with open(file, 'w', encoding='utf-8') as fp:
            json.dump(i, fp=fp, ensure_ascii=False)
            print(file, "写入完成")

    jsonfile = "D:/PycharmProjectsuntitled/webCrawler\\baihehua_img\\json"
    # 获取json文件夹文件集
    dirs = os.listdir(jsonfile)
    for i in dirs:
        # 读取各个json文件
        with open(jsonfile + '/' + i, "r", encoding='utf-8') as f:
            data = json.load(f)
        # 一层级文件夹
        filet = data['title']
        # va1 代表分组路径
        va1 = os.getcwd() + '/' + filet
        isExists = os.path.exists(va1)
        # 创建目录
        if not isExists:
            os.makedirs(va1)
        # 妹子组
        meizilist = data['g']
        for i in meizilist:
            print(i['filename'])
            print(i['href'])
