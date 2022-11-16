import requests,ssl,re,time,os,json
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
#headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE", "Accept-Encoding":"gzip","Connection": "close"} 
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36", "Accept-Encoding":"gzip","Connection": "close"} 
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
else:
    exit(1)

writer_books_chapters_contents = {}
for writer,bookdict in writer_books_chaptersurl.items():
    if writer != '李亮':
        continue
    writer_books_chapters_contents[writer] = {}
    try:
        for b, culist in bookdict.items():
            writer_books_chapters_contents[writer][b] = {}
            for cu in culist:
                _, url = cu # _ = chap_name, not used because some chapter has a parent big-chapter name
                if _ == '李亮':
                    continue
                soup = get_soup(url, 0.5)
                header = soup.find('font', color="#000000", size="4").text.replace('\xa0',' ') #<font color="#000000" size="4">
                text = soup.get_text()
                writer_books_chapters_contents[writer][b][header] = re.findall(re.compile('\r\n\xa0\xa0\xa0\xa0(.*?)\n'),text)
    except Exception as e:
        print("Error occured. Please rerun and continue. -- ",e)
        exit(1)
    json.dump(writer_books_chapters_contents[writer], open(writer+'.json','w',encoding='utf8'), ensure_ascii=False)
    print(writer+" done.")

#json.dump(writer_books_chapters_contents, open('authers_books_chapters_paragraphs.json','w',encoding='utf8'), ensure_ascii=False)

