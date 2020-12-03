import os
import requests
import time
import json
from bs4 import BeautifulSoup


def main():
    base_url = 'https://www.bhhzw.com/'
    headers = {
        "Referer": base_url,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
    }
    # 初始化应用程序
    Application = BaiHe(base_url, headers, 5)
    print("\t程序初始化完成")
    # 运行程序
    print("\t程序开始运行")
    Application.run()


class BaiHe(object):
    def __init__(self, url, header, timeout=3):
        # 入口url
        self.url = url
        # 浏览器头信息
        self.header = header
        # 全局控制超时响应
        self.timeout = timeout
        # 脚本资源路径
        self.path = os.getcwd()
        # 获取标记体
        self.mark = self.markinfo()

    # 获取标记对象
    def markinfo(self):
        mark_path = self.path + '/mark.json'
        isExists = os.path.exists(mark_path)
        if not isExists:
            return None
        try:
            with open(mark_path, 'r+', encoding='utf-8') as mark:
                mark = json.load(mark)
        except Exception as E:
            print("\t标记文件出错" + E)
        print("\t启动前获取标记")
        return mark

    # 创建栏目的json文件
    def run(self):
        text = requests.get(self.url, headers=self.header).text
        soup = BeautifulSoup(text, 'lxml').select(".nav")[0]
        ul = soup.find_all('li')
        # 栏目列表
        category = []
        for li in ul:
            # 获取栏目的页数
            html = requests.get(li.a['href'], headers=self.header).text
            soup = BeautifulSoup(html, 'lxml').select(".page-navigator")[0]
            page = soup.find_all("li")[-2]
            # 获取每一个栏目的总页数 最大限制在30
            page = 30 if int(page.string) > 50 else int(page.string)
            data = {"title": li.string, "href": li.a['href'], "pages": page}
            category.append(data)
            # 爬取栏目
            print("正在爬取\t" + li.string + "页数.......有" + str(page) + "页")
        self.writer_json(category)
        self.reader_json()

    # 主要写入程序
    def writer_json(self, cates):
        print("开始写入json数据--------》》")
        for item in cates:
            url = item["href"]
            page = item["pages"]
            authors = []
            # for index in range(1, page + 1):
            for index in range(1, page+1):
                # 页面轮询
                page_url = url + str(index)
                time.sleep(3)
                text = requests.get(page_url, headers=self.header).text
                items = BeautifulSoup(text, 'lxml').select(".item-link")
                # 获取作者地址
                author = get_authors(items)
                authors = authors + author
            item['count'] = len(authors)
            item['g'] = authors
            # 写入json
            jsondir = self.path + '/jsons/'
            file = jsondir + item['title'] + ".json"
            # 创建json文件夹
            createdir(jsondir)
            # 写入文件
            write(file, item)
            print(item["title"] + "\t写入成功")

    # 读取json文件
    def reader_json(self):
        dirs = self.path + "/jsons"
        files = os.listdir(dirs)
        for file in files:
            path1 = dirs + "/" + file
            data = read(path1)
            # 一层级文件夹
            folder_name = data['title']
            file_path = self.path + '/mm/' + folder_name
            # 创建一级文件夹
            print("创建文件夹" + folder_name)
            createdir(file_path)
            # 妹子单独
            meizi_list = data['g']
            self.download_img(meizi_list, file_path, folder_name)

    def download_img(self, gorup, path, title):
        start = 0 if not self.mark else self.mark[title]['index']
        if not self.mark:
            # 创建mark标记 ,第一次全部创建
            self.mark = createmark()
        # 路径转义
        for index in range(start, len(gorup)+1):
            va1 = gorup[index]['filename']
            href = gorup[index]['href']
            filename = va1.strip()
            meizidir = path + '/' + filename
            # 创建妹子文件夹
            createdir(meizidir)
            time.sleep(3)
            text = requests.get(href, headers=self.header).text
            img = BeautifulSoup(text, 'lxml').select('#masonry div img')
            imgs = []
            for data in img:
                imgs.append(data['data-original'])
            i = 1
            for url_img in imgs:
                img_data = requests.get(url_img, headers=self.header)
                file_name = str(i) + '.jpg'
                img_path = meizidir + '/' + file_name
                try:
                    with open(img_path, 'wb') as f:
                        f.write(img_data.content)
                        print("\t|" + file_name + '\tSuccessful')
                except Exception as E:
                    print("图片下载失败原因:" + E)
                    self.mark[title]['index'] = index
                    write(self.path, self.mark)
                    exit(-1)
                i += 1


# 获取每一位作者的地址
def get_authors(items):
    authors = []
    for p in items:
        author = {}
        filename = p.div.string
        href = p['href']
        author['filename'] = filename.replace("\n", "")
        author['href'] = href
        print(author['filename']+'\t'+author['href'])
        authors.append(author)
    return authors


# 创建文件夹
def createdir(path):
    isExists = os.path.exists(path)
    # 创建目录
    try:
        if not isExists:
            os.makedirs(path)
    except Exception as E:
        print("文件创建失败:" + E)


# 写json文件
def write(path, text):
    try:
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(text, fp=fp, ensure_ascii=False)
    except Exception as E:
        print("json文件写入失败,失败文件" + path + "\n失败原因:" + E)
        return


# 读json文件
def read(path):
    try:
        with open(path, "r", encoding='utf-8') as fp:
            data = json.load(fp)
    except Exception as E:
        print("json文件读取失败,读取失败文件" + path + "\n失败原因:" + E)
        return
    return data


# 创建mark标记文件
def createmark():
    data = {}
    dirs = os.getcwd() + "/jsons"
    files = os.listdir(dirs)
    for title in files:
        title = title[:4]
        data[title] = {"index": 0}
    return data

if __name__ == '__main__':
    main()
