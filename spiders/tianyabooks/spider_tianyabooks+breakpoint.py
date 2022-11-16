import requests,ssl,re,time,os,json
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE", "Accept-Encoding":"gzip","Connection": "close"} 
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

baseUrl = 'https://wx.tianyabooks.com'

writer_url = {}
if os.path.exists('writer_url.json'):
    writer_url = json.load(open('writer_url.json','r',encoding='utf8'))
else:
    URL = 'https://wx.tianyabooks.com/writer.html'
    soup = get_soup(URL, 0)
    res = soup.find_all('a',href=re.compile('writer/(.*?).html'))
    for r in res:
        writer = r.get_text()
        _url = r.get('href')
        url = baseUrl + _url
        writer_url[writer] = url
    json.dump(writer_url, open('writer_url.json','w',encoding='utf8'), ensure_ascii=False)

'''
writer_url = {'xxx': urlx, 'yyy': urly}
writer_books_url = {'xxx': [(book1,url1), (book2,url2)], 'yyy': ...}
writer_books_chaptersurl = {'xxx': {book1: [(chapter1,url1), ...], book2: [(chapter1,url1), ...], ...}}
writer_books_chapters_contents = {'xxx': {book1: {chapter1: [para1, para2, ...], chapter2: [...]}, book2: ...}}
'''
writer_books_url = {}
if os.path.exists('writer_books_url.json'):
    writer_books_url = json.load(open('writer_books_url.json','r',encoding='utf8'))
else:
    for writer,u in writer_url.items():
        soup = get_soup(u, 0.5)
        books = soup.find_all('a',href=re.compile('book/(.*?)'),target="_blank")
        writer_books_url[writer] = []
        for b in books:
            book_name = b.get_text()
            _url = b.get('href')
            url = baseUrl + _url
            writer_books_url[writer].append((book_name, url))
    json.dump(writer_books_url, open('writer_books_url.json','w',encoding='utf8'), ensure_ascii=False)

writer_books_chaptersurl = {}
if os.path.exists('writer_books_chaptersurl.json'):
    writer_books_chaptersurl = json.load(open('writer_books_chaptersurl.json','r',encoding='utf8'))
else:
    if os.path.exists('writer_books_chaptersurl_checkpoint.json'):
        writer_books_chaptersurl = json.load(open('writer_books_chaptersurl_checkpoint.json','r',encoding='utf8'))
    for writer,bulist in writer_books_url.items():
        if writer in writer_books_chaptersurl:
            continue
        writer_books_chaptersurl[writer] = {}
        try:
            for bu in bulist:
                b, u = bu
                writer_books_chaptersurl[writer][b] = []
                soup = get_soup(u, 0.5)
                chapters = soup.find_all('a',href=re.compile('\d{1}.html'))
                for c in chapters: # one chapter per page, i.e. next page is next chapter.
                    chap_name = c.get_text()
                    _url = c.get('href')
                    content_url = u + _url
                    writer_books_chaptersurl[writer][b].append((chap_name, content_url))
        except Exception as e:
            print("Error occured. Checkpoint saved to: writer_books_chaptersurl_checkpoint.json -- ",e)
            exit(1)
        print(writer+" chapter_names of all books OK.")
        json.dump(writer_books_chaptersurl, open('writer_books_chaptersurl_checkpoint.json','w',encoding='utf8'), ensure_ascii=False)
    json.dump(writer_books_chaptersurl, open('writer_books_chaptersurl.json','w',encoding='utf8'), ensure_ascii=False)
        
writer_books_chapters_contents = {}
authers_done_checkpoint = []
for writer,bookdict in writer_books_chaptersurl.items():
    if writer+'.json' in os.listdir('.'):
        continue
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

