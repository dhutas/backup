#nohup python3 -u spider_fromOnePoint.py > out.log 2>&1 &
import requests,ssl,re,time,os,json
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE", "Accept-Encoding":"gzip","Connection": "close"} 
ssl._create_default_https_context = ssl._create_unverified_context
#requests.DEFAULT_RETRIES = 5  
s = requests.session()
s.keep_alive = False  

CHECK_NUM = 2000
alldata = dict()
doneIds = set()
errorIds = set()
todoIds = set()
baseUrl = "https://jikipedia.com/definition/"
#startId = "1058299323"
#url = baseUrl+startId

# 隧道域名:端口号
tunnel = "tps110.kdlapi.com:15818"
'''
# 用户名密码方式
username = "t13259056202155"
password = "xso0lfj6"
proxies = {
    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
}
'''
# 白名单方式（需提前设置白名单）
proxies = {
    "http": "http://%(proxy)s/" % {"proxy": tunnel},
    "https": "http://%(proxy)s/" % {"proxy": tunnel}
}

def getBreakPoint():
    global alldata, todoIds, doneIds, errorIds
    if os.path.exists("ids_done.txt"):
        with open("ids_done.txt",'r') as f:
            doneIds = {i.strip() for i in f.readlines()}
    if os.path.exists("ids_error.txt"):
        with open("ids_error.txt",'r') as f:
            errorIds = {i.strip() for i in f.readlines()}
    if os.path.exists("ids_done.txt"):
        with open("ids_todo.txt",'r') as f:
            todoIds = {i.strip() for i in f.readlines()}
    if os.path.exists("alldata.json"):
        alldata = json.load(open("alldata.json",'r'))

def setBreakPoint():
    global alldata, todoIds, doneIds, errorIds
    with open("ids_done.txt",'w') as f:
        _ = f.write('\n'.join(doneIds))
    with open("ids_error.txt",'w') as f:
        _ = f.write('\n'.join(errorIds))
    with open("ids_todo.txt",'w') as f:
        _ = f.write('\n'.join(todoIds))
    json.dump(alldata, open('alldata.json','w',encoding='utf8'), ensure_ascii=False)

def getResponse(url, delay=0):
    time.sleep(delay)
    id = url.split('/')[-1]
    try:
        r = requests.get(url,headers=headers,verify = False, timeout=10, proxies=proxies)
        status = r.status_code
        if status != 200:
            print("[-] status_code: "+status+'\t'+id)
            return status, ''
        content = r.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        #print(soup.prettify())
        return status, soup
    except:
        print("[-] no response: \t"+id)
        return 1, ''

def getInfo(soup):
    soupTarget = soup.find(class_=re.compile("full-card container"))
    viewcount = soupTarget.find(class_=re.compile("view basic-info-element")).get_text().strip()
    createdate = soupTarget.find(class_=re.compile("created basic-info-element")).get_text().strip()
    author = soupTarget.find(class_=re.compile("author-name name")).get_text().strip()
    title = soupTarget.find(class_=re.compile("title-container-content")).get_text().strip()
    content = soupTarget.find(class_="content").get_text().replace('\u200b','').replace('\u200c','')
    images = []
    for img in soupTarget.find_all(class_=re.compile("show-images-img")):
        images.append(img.get('src'))
    tags = []
    soupTags = soupTarget.find(class_="tag-list tags")
    for tag in soupTarget.find_all(class_=re.compile("tag-list-item")):
        tags.append(tag.get_text().strip())
    likecount = ''
    thumpcount = ''
    for like in soupTarget.find_all(class_=re.compile("like button")):
        _like = like.get_text()
        if '赞' in _like:
            thumpcount = _like.replace('赞','').strip()
        elif '收' in _like:
            likecount = _like.replace('收藏','').strip()
        else:
            print("[!] 点赞收藏标签出现异常："+_like+'\t'+title)
    data = {'标题': title, '日期': createdate, '作者': author, '访问': viewcount, '收藏': likecount, '点赞': thumpcount, '内容': content, '图片': images, '标签': tags}
    return data

def getOtherIds(soup):
    others = soup.find(class_="definitions")
    ids = []
    try:
        for item in others.find(class_="masonry"):
            ids.append(item.get('data-id'))
    except:
        print("[?] no other ids: \t"+id)
    return ids

def run(url):
    global alldata, todoIds, doneIds, errorIds
    id = url.split('/')[-1]
    status, soup = getResponse(url, 0)
    if status!=200:
        errorIds.add(id)
        return 1
    try:
        alldata[id] = getInfo(soup)
        doneIds.add(id)
    except:
        print("[!] 状态200但疑似被反爬："+'\t'+id)
        errorIds.add(id)
        return 2
    ids = getOtherIds(soup)
    todoIds = todoIds.union(set(ids))
    return 0

getBreakPoint()
count = 1
QUITFLAG = False
while(True):
    try:
        if len(todoIds)==0:
            break
        _todoIds = todoIds.copy()
        for id in _todoIds:
            url = baseUrl+id
            ret = run(url)
            if ret == 2: # 疑似被反爬
                QUITFLAG = True
                break
            todoIds.remove(id)
            count += 1
        if count%CHECK_NUM==0 or QUITFLAG:
            print('[+] checkpoint saved. Done: {d}  Error: {e}  Todo: {t}'.format(d=len(doneIds),e=len(errorIds),t=len(todoIds)))
            setBreakPoint()
            if QUITFLAG:
                break
    except:
        print('[-] error. checkpoint saved. Done: {d}  Error: {e}  Todo: {t}'.format(d=len(doneIds),e=len(errorIds),t=len(todoIds)))
        setBreakPoint()
        break
