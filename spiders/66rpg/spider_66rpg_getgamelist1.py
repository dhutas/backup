import requests,ssl,re,time,os,json
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
        if data.status_code == 200:
            data.encoding = "utf-8" #data.apparent_encoding
            html = data.text
            return BeautifulSoup(html, 'html.parser')
        else:
            return data.status_code
    except:
        delay += 5
        if delay > 20:
            print("Sorry, I stop trying with too many times.")
            exit(1)
        print("Try it after %d seconds: %s"%(delay,url))
        get_soup(url, delay)

baseUrl = 'https://www.66rpg.com/game/'

id_name_ver_desc_tags = {}
CHECK_NUM = 1000
check_num = 0
if os.path.exists('id_name_ver_desc_tags1_checkpoint.json'):
    id_name_ver_desc_tags = json.load(open('id_name_ver_desc_tags1_checkpoint.json','r',encoding='utf8'))
for id in range(158000,450000): 
    if id in id_name_ver_desc_tags:
        continue
    try:
        soup = get_soup(baseUrl+str(id), 0)
        if soup == 404:
            continue
        elif isinstance(soup, int):
            print(id, "status_code: ", soup)
            continue
        elif '登录' in soup.find("title").text:
            continue
        try:
            title = soup.find('span',title=re.compile('.*?')).text
        except:
            title = '-'
        try:
            desc = soup.find('div', attrs={"class":"content game_des_content"}).text.strip() #<div class="content game_des_content">...</div>
        except:
            desc = '-'
        try:
            tags = [t.text for t in soup.find_all('a', href=re.compile("/list/tag/tid/\d{1}"), target="_blank")] #<a href="/list/tag/tid/5" target="_blank">...</a>
        except:
            tags = '-'
        id_name_ver_desc_tags[str(id)] = {'n':title, 'd':desc, 't': tags} # dict key must be string, if not, it will be string when json.load from file, but int in newer dict items
        print(id, title)
        check_num += 1
        if check_num%CHECK_NUM == 0:
            json.dump(id_name_ver_desc_tags, open('id_name_ver_desc_tags1_checkpoint.json','w',encoding='utf8'), ensure_ascii=False)
            print("[num = %d] Checkpoint saved to: id_name_ver_desc_tags1_checkpoint.json"%check_num)
    except Exception as e:
        #print("Error occured. Checkpoint saved to: id_name_ver_desc_tags_checkpoint.json -- ",e)
        print("[-] Error: ",e)
        continue
    
json.dump(id_name_ver_desc_tags, open('id_name_ver_desc_tags1.json','w',encoding='utf8'), ensure_ascii=False)
        
