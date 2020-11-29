# coding＝utf-8
import requests
import re
import os
import json
import time


class Getlinks(object):
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
        }
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.path = self.dir_path + '/json'
        DirectoryisExists = os.path.exists(self.path)
        # 创建目录
        if not DirectoryisExists:
            os.makedirs(self.path)
        print("\t| 初始化完成")

    # 解析url地址
    def ParseUrl(self):
        for i in self.url:
            # 抓取电影链接
            print("\t| 开始抓取页面跳转链接")
            links = self.GetLinks(i)
            print("\t| " + i['catgory'] + "页面链接抓取完成")
            print("\t| 开始收集电影下载链接数据")
            info = self.Getinfo(i['catgory'], links)
            print("\t| " + i['catgory'] + "页面收集完成")
            WriterJson(info, i['catgory_as'])
            print("\t| 文件写入完成")

    # 抓取详情页链接
    def GetLinks(self, group):
        name = group['catgory']
        url = group['url']
        count = group['count']
        # 第一组url链接不规则做分步处理
        if "400" in name:
            return self.GetLink(url, count, 1)
        else:
            return self.GetLink(url, count)

    # 获取所有链接
    def GetLink(self, url, count, flag=0):
        time.sleep(1)
        totalurl = []
        if flag == 1:
            for i in range(1, count+1):
                print("第" + str(i) + "页数据")
                suffix = '.html' if i == 1 else '_' + str(i) + '.html'
                base_url = url + suffix
                # 抓取本页的超链接
                try:
                    res = requests.get(base_url, headers=self.headers).text
                    links = re.findall(r'http[s]?://www.ygdy8.com/html/gndy/.*?.html', res, re.S)
                    # 去重
                    links = list(set(links))
                    totalurl += links
                except Exception:
                    continue
            return totalurl
        else:
            for i in range(1, count + 1):
                print("第" + str(i) + "页数据")
                base_url = url + str(i) + '.html'
                # 抓取本页的超链接
                try:
                    res = requests.get(base_url, headers=self.headers).text
                    # 过滤其他文本
                    re_rule = 'class="co_content8"(.*?)</div>'
                    context = ReMatch(re_rule, res)
                    try:
                        links = re.findall(r'/html/gndy/dyzz/[^in].*?.html', context, re.S)
                    except BaseException as E:
                        print('没有匹配的数据')
                        continue
                    totalurl += links
                except Exception as E:
                    print('抓取失败的原因:' + E)
                    continue
            for i in range(len(totalurl)):
                # 添加前缀
                totalurl[i] = 'https://www.dytt8.net' + totalurl[i]
            return totalurl

    # 抓取电影信息
    def Getinfo(self, catgroy, links):
        info_json = {"catgory": catgroy, "count": len(links), "group": []}
        # 循环请求网页
        for url in links:
            temp = {}
            try:
                res = requests.get(url, headers=self.headers).text
                title_re = '<div class="title_all">(.*?)</div>'
                title = ReMatch(title_re, res)
                rule = '#07519a>(.*?)</font></h1>'
                title = ReMatch(rule, title)
                title = title.encode('ISO-8859-1').decode('gbk')
                rule = '#fdfddf(.*?)</a>'
                filelink = ReMatch(rule, res)
                filelink = filelink.encode('ISO-8859-1').decode('gbk')
                rule = '<a href="(.*?)"'
                filelink = ReMatch(rule, filelink)

                print(title)
                print(filelink)

                # 添加纠错机制
                if not CheckVirtual(filelink):
                    continue
                temp["title"] = title
                temp["filelink"] = filelink
                info_json["group"].append(temp)

            except Exception:
                print("The site 404")
                continue
        return info_json


# 文本匹配
def ReMatch(rule, res):
    return re.compile(rule, re.S).findall(res)[0]


# 将数据存储在json文件中
def WriterJson(info_json, json_name):
    json_name = json_name
    # 将字典转换成json字符串
    # 在Python3.7中 使用json.dumps 不转码 ensure_ascii
    str_json = json.dumps(info_json, ensure_ascii=False, indent=4)
    try:
        with open('./json/' + json_name + '.json', 'w', encoding='utf-8') as f:
            f.write(str_json)
    except Exception as E:
        print("写入文件出错" + E)
        f.close()
        return


# 无效链接检查处理
def CheckVirtual(url):
    return True if 'ftp' in url else False


if __name__ == '__main__':
    # 初始化爬取栏目数据
    base_url_list = [
        {
            "catgory": "IMDB评分8分左右影片400多部",
            "catgory_as": "imdb",
            "url": "https://www.dytt8.net/html/gndy/jddy/20160320/50523",
            "count": 4
        },
        {
            "catgory": "最新电影",
            "catgory_as": "zuixin",
            "url": "https://www.dytt8.net/html/gndy/dyzz/list_23_",
            "count": 20
        },
        {
            "catgory": "欧美电影",
            "catgory_as": "oumei",
            "url": "https://www.dytt8.net/html/gndy/oumei/list_7_",
            "count": 30
        },
        {
            "catgory": "国内电影",
            "catgory_as": "china",
            "url": "https://www.dytt8.net/html/gndy/china/list_4_",
            "count": 30
        },
        {
            "catgory": "日韩电影",
            "catgory_as": "rihan",
            "url": "https://www.dytt8.net/html/gndy/rihan/list_6_",
            "count": 30
        }
    ]
    Context = Getlinks(base_url_list)
    Context.ParseUrl()
