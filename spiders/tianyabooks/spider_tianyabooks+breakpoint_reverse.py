import requests,ssl,re,time,os,json
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
#headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE", "Accept-Encoding":"gzip","Connection": "close"} 
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36", "Accept-Encoding":"gzip","Connection": "close"} 
ssl._create_default_https_context = ssl._create_unverified_context
requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接
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

writer_books_chaptersurl = {}
if os.path.exists('writer_books_chaptersurl.json'):
    writer_books_chaptersurl = json.load(open('writer_books_chaptersurl.json','r',encoding='utf8'))

writer_books_chapters_contents = {}
wbc = []
for w,bd in writer_books_chaptersurl.items():
    wbc.append((w,bd))

i = -1
while(True):
    writer,bookdict = wbc[i]
    i-=1
    if writer+'.json' in os.listdir('.'):
        break
    writer_books_chapters_contents[writer] = {}
    try:
        for b, culist in bookdict.items():
            writer_books_chapters_contents[writer][b] = {}
            for cu in culist:
                _, url = cu # _ = chap_name, not used because some chapter has a parent big-chapter name
                soup = get_soup(url, 0)
                header = soup.find('font', color="#000000", size="4").text.replace('\xa0',' ') #<font color="#000000" size="4">
                text = soup.get_text()
                writer_books_chapters_contents[writer][b][header] = re.findall(re.compile('\r\n\xa0\xa0\xa0\xa0(.*?)\n'),text)
                print(writer, b, _, url)
    except Exception as e:
        print(writer," ---- Error occured. Please redump this author. ---- ",e)
        continue #exit(1)
    json.dump(writer_books_chapters_contents[writer], open(writer+'.json','w',encoding='utf8'), ensure_ascii=False)
    print(writer+" ============================= done.")

#json.dump(writer_books_chapters_contents, open('authers_books_chapters_paragraphs.json','w',encoding='utf8'), ensure_ascii=False)

