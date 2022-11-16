import requests,ssl,re,time,os,json,sys
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE", "Accept-Encoding":"gzip","Connection": "close"} 
ssl._create_default_https_context = ssl._create_unverified_context
requests.DEFAULT_RETRIES = 5  
s = requests.session()
s.keep_alive = False  
def get_soup(url, delay): # delay some seconds
    time.sleep(delay)
    try:
        data = requests.get(url,headers=headers,verify = False)
        data.encoding = data.apparent_encoding
        html = data.text
        return BeautifulSoup(html, 'html.parser')
    except:
        delay += 5
        if delay > 20:
            print("Sorry, I stop trying with too many times.")
            exit(1)
        print("Try it after %d seconds: %s"%(delay,url))
        get_soup(url, delay)

baseUrl = 'https://www.fx361.com/'
bkUrl = 'bk/*/#.html' # *=xxsyk, #=20061

if len(sys.argv) != 3:
    print('python %s BookName EndDate\n for example:\n\tpython %s xxsyk 20219'%(sys.argv[0]))
    exit(1)

BookName = sys.argv[1]
bkUrl = bkUrl.replace('*', BookName)
EndDate = sys.argv[2]
issue = []
for y in range(2006,2021+1):
    issue.extend([str(y)+str(m) for m in range(1,12+1)])
assert EndDate in issue
'''
"来源":
{
    "期号":[{
        "l":"栏目",
        "t":"题目",
        "z":"作者",
        "k":["关键词","…"],
        "n":["内容","..."]}, {…} ]
}

'''
checkperiod = 12
cp = 0
data = {}
if os.path.exists(BookName+'.json'):
    data = json.load(open(BookName+'.json','r',encoding='utf8'))
else:
    if os.path.exists(BookName+'_checkpoint.json'):
        data = json.load(open(BookName+'_checkpoint.json','r',encoding='utf8'))
    for iss in issue:
        if iss == EndDate:
            break
        url = baseUrl + bkUrl.replace('#', iss)
        if iss in data:
            continue
        data[iss] = []
        cp += 1
        try:
            soup = get_soup(url, 0)
            lanmus = soup.find('div',id='dirList').find_all(attrs={'class':'dirItem02'})
            for lm in lanmus:
                _data = {}
                _data["l"] = lm.find('h5').text
                timus = lm.find_all('a',href=re.compile('/page/(.*?)'))
                for tu in timus:
                    u = tu.get('href')
                    _data["t"] = tu.get('title')
                    _url = baseUrl + u[1:]
                    content = get_soup(_url,0)
                    _data["k"] = [tag.text for tag in content.find(attrs={'class':"article_keyword"}).find_all('a')]
                    try:
                        _data["z"] = content.find(attrs={'class':"time_source"}).find_all('span')[1].text
                    except:
                        _data["z"] = "佚名"
                    _data["n"] = [con.text for con in content.find(attrs={'class':'txt'}).find_all('p')[1:]]
                    data[iss].append(_data)
        except Exception as e:
            print(iss," --Error-- ",e)
            continue
        print(iss," OK!")
        if cp%checkperiod == 0:
            json.dump(data, open(BookName+'_checkpoint.json','w',encoding='utf8'), ensure_ascii=False)
    json.dump(data, open(BookName+'.json','w',encoding='utf8'), ensure_ascii=False)
        

