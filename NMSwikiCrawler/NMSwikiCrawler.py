# 2020-03-22版
# 爬取无人深空wiki上的所有物品和配方

# 防反爬：
# （1）多伪造一些浏览器
# （2）爬取的频率不能过高，间隔至少要大于1s 
# （3）设置随机间隔，（1~10s之间）
# （4）把之前已经爬过的页面做一个记录，重新爬取的时候不再爬之前爬过的页面


import requests
from urllib.request import unquote
from bs4 import BeautifulSoup
import html5lib
import time
import random

#伪造header
def random_headers():
    user_agents = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'
    ]
    headers = {'User-Agent':random.choice(user_agents)}
    return headers

def getPage(url, timeout):
    r = requests.get(url=url, headers=random_headers(), timeout=timeout)
    if r.status_code == requests.codes.ok:  # 返回200
        r.encoding = 'utf-8'
        return r.text
    else:
        return None


def downloadImg(url, name):
    img = requests.get(url)
    data = img.content
    imgName = url[url.rfind('/')+1:url.rfind('.')]
    suffix = url[url.rfind('.'):]
    with open('./spider_picture/'+imgName+name+suffix, 'wb') as fb:
        fb.write(data)
    fb.close()


def writeText(type, text):
    with open('./spider_text/'+type+'.txt', 'a', encoding='utf-8') as fb:
        fb.write(text)
    fb.close()

# 抓取主页，下载五张大类图片
def parseMain(baseUrl, mainUrl):
    html = getPage(baseUrl+mainUrl, 30)
    soup = BeautifulSoup(html, 'html5lib')
    # 5个产品类别
    types = soup.find("div", attrs={"class": "col-md-6"})\
        .find(text="游戏数据").parent.parent\
        .find_all("li", attrs={"class": "gallerybox"})

    dic = {}  # 字典里存放(大类名: 大类url)的映射
    for t in types:
        node = t.find(title=True)
        name = node.string  # 大类名
        url = unquote(node.get("href"))  # 大类URL
        #print(name+": "+url)
        dic[name] = url
        imgUrl = t.find("img").get("src")  # 大类别图片
        # 下载图片
        downloadImg(imgUrl, name)
    return dic


# 抓取大类别页面，不写文件，不存图片
def parseType(baseUrl, typeUrl):
    html = getPage(baseUrl+typeUrl, 30)
    soup = BeautifulSoup(html, 'html5lib')  # html5lib和浏览器的解析方式相同，是最好的解析器
    table = soup.find(
        "table", class_="nowraplinks mw-collapsible mw-autocollapse navbox-inner").tbody
    rows = table.find_all("tr", style=False)
    urlSet = set()  # 用set保存每个大类下的物体页面URL,因为会有重复的url
    for r in rows[1:]:
        # 获得子类别名（表头）
        tName = r.th.string
        if tName == "浓缩物质": # 不要浓缩物质
            continue
        # 获得cell
        elements = r.td.div.contents
        for e in elements:
            if e.name == "span":
                a = e.contents[1]
                #name = a.string
                url = unquote(a.get("href"))
                #print(name+': '+url)
                if url[:6] == "/wiki/":  # 有的物品没有单独的页面，丢掉这样的物品
                    urlSet.add(url)
    return urlSet


# 抓取物品页面，写文本，存图片
# 参数3：大类名（不是url）
def parseItem(baseUrl, objUrl, type):
    html = getPage(baseUrl+objUrl, 30)
    soup = BeautifulSoup(html, 'html5lib')
    objText = ''    # 对象文本
    formulaText = ''    # 配方文本

    # 抓取对象数据
    objTable = soup.find("table", class_="infobox")
    if objTable == None: #有些物品有自己的页面，但是没人编辑！
        return
    objTable = objTable.tbody
    # print(objTable.prettify())
    ts = objTable.find_all(text=True)
    for t in ts:
        if t[0] == '\n':
            objText+=t[1:]+' '
        else:
            objText += t+' '
    objText += type + '\n'
    ch_name = objTable.contents[0].th.big.string  # 中文名
    imgNode = objTable.contents[1].td.img
    if imgNode != None:
        imgUrl = imgNode.get("src")  # 图片URL
    else:   # 有的物品没图片
        imgUrl = None

    # 抓取配方数据
    section = soup.find("div", class_="mw-parser-output").contents
    for sec in section:
        if sec.name == "h2":  # 二级标题
            formulaText += sec.span.string+'\n'
        elif sec.name == "ul":  # 列表
            for li in sec.contents: #每个列表项的文本占一行
                if li.name == "li":
                    texts = li.find_all(text=True)
                    for t in texts:
                        formulaText += t
                    formulaText += '\n'
            formulaText += '\n'
        elif sec.name == "p": #普通段落
            texts = sec.find_all(text=True)
            for t in texts:
                formulaText += t
            formulaText += '\n'
    #print(formulaText)
    # 写入对象和配方
    writeText('obj', objText)
    writeText('formula', formulaText)
    # 下载图片
    if imgUrl!= None:
        time.sleep(random.randint(1,10))    #sleep
        downloadImg(imgUrl, ch_name)


def main():
    # 读入已抓取过的页面
    alreadyGet = set()
    with open('./urls.txt', 'r', encoding='utf-8') as fb:
        for line in fb:
            if line != "":
                alreadyGet.add(line[:-1])
    fb.close()

    baseUrl = 'https://nms.huijiwiki.com'
    mainUrl = '/wiki/首页'
    #从首页开始爬
    print("正在提取："+baseUrl+mainUrl)
    dic = parseMain(baseUrl, mainUrl)
    time.sleep(random.randint(1,10))    #sleep
    for type in dic.keys():
        print("正在提取："+baseUrl+dic[type])
        urls = parseType(baseUrl, dic[type])
        time.sleep(random.randint(1,10))    #sleep
        for u in urls:
            if u not in alreadyGet: # 判断是否已经抓取过
                print("正在提取："+baseUrl+u)
                parseItem(baseUrl, u, type)
                # 记录已经抓取过的url
                with open('./urls.txt', 'a', encoding='utf-8') as fb:
                    fb.write(u+'\n')
                fb.close()
                time.sleep(random.randint(1,10))    #sleep


if __name__ == '__main__':
    main()

