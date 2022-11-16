#https://github.com/ssz66666/66rpg-spoofer/     <-- old method
#https://github.com/PeaShooterR/fuck66rpg       <-- Thank you!
import urllib3, json, base64, re, os, gc, time

FLAG_I = [-1,1,1,1,1]


def get_mapbin(guid, ver, http, recur=20):
    if recur < 1:
        return ver, None
    mapBin = http.request('GET', 'http://wcdn1.cgyouxi.com/web/' + guid + '/' + ver + '/Map.bin').data
    if 'Error' in str(mapBin[:50]):
        ver = str(int(ver) - 1)
        if int(ver) < 1:
            return ver, None
        recur -= 1
        return get_mapbin(guid, ver, http, recur) # must use return in head of recurrence function
    else:
        return ver, mapBin

def get_gamebin(gindex):
    if not isinstance(gindex, str):
        gindex = str(gindex)
    http = urllib3.PoolManager()
    gameLink = 'https://www.66rpg.com/f/' + gindex + '/ref/d3d3LjY2cnBnLmNvbQ=='
    body = str(http.request('GET', gameLink).geturl())
    guidIndex = body.find('guid=') + 5
    guid = body[guidIndex:guidIndex + 32]
    body = http.request('GET', 'http://www.66rpg.com/api/common/versions?guid=' + guid).data
    jsonLoads = json.loads(body)
    gameName = str(jsonLoads['data'][-1]['name'])
    latestVer = str(jsonLoads['data'][-1]['version'])
    ver = latestVer
    # 通过guid+ver获取Map.bin
    # http://wcdn1.cgyouxi.com/web/$guid$/$ver$/Map.bin
    # 也可以使用网页客户端API下载压缩过后的游戏资源，格式json
    # https://cgv2.66rpg.com/api/oapi_map.php?action=create_bin&guid=$guid$&version=$ver$&quality=32
    # 解析map.bin中的文件名与MD5
    lowercasefileName = []
    MD5 = []
    # Map.bin以「?? ?? 00 00 0D 00 00 00」开头，文件名与MD5以「?? ?? ?? 00 20 00 00 00」分隔，每行之间以「?? 00 00 00」分隔
    # 文件大致为「?? ?? 00 00 0D 00 00 00 文件名_1 ?? ?? ?? 00 20 00 00 00 MD5_1 ?? 00 00 00 文件名_2.....」编码UTF-8
    # 先分前者再分后者
    while(True):
        ver, mapBin = get_mapbin(guid, ver, http)
        if mapBin != None:
            break
        else:
            print(gindex+'_'+ver+'_failed')
            return None
    # print('http://wcdn1.cgyouxi.com/web/' + guid + '/' + ver + '/Map.bin')
    mapbinHex = base64.b16encode(mapBin).decode()
    mapbinHex = mapbinHex[16:]  # 切掉文件头
    # 分割文件名和MD5，并保证后半部分剩余的hex不是奇数。否则 X[X XX XX X0 02 00 00 00 0]X 会匹配错误
    mapbinHex = re.sub('......0020000000(?!.(..)*$)', '0D0A', mapbinHex)
    mapbinHex = re.sub('..000000(?!.(..)*$)', '0D0A', mapbinHex)  # 分割行，并保证后半部分剩余的hex数据不是奇数。理由同上。
    FLAG = False
    try:
        mapbinUTF8 = base64.b16decode(mapbinHex.encode()).decode('UTF-8')
    except:
        mapbinUTF8 = base64.b16decode(mapbinHex.encode()).decode('unicode_escape')#('UTF-8')
        FLAG = True
    mapbinUTF8 = str.split(mapbinUTF8, '\r\n')
    lowercasefileName = mapbinUTF8[::2]  # 取偶数项
    MD5 = mapbinUTF8[1::2]  # 取奇数项
    # 更正fileName大小写
    fileName = []
    for name in lowercasefileName:
        name = name.replace('audio/bgm/', 'Audio/BGM/')
        name = name.replace('audio/se/', 'Audio/SE/')
        name = name.replace('audio/voice/', 'Audio/Voice/')
        name = name.replace('audio/bgs/', 'Audio/BGS/1')
        # name = name.replace('data/game.bin', 'Data/Game.bin')
        name = name.replace('data/game.bin', 'data/Game.bin')
        # name = name.replace('data/map.bin', 'Data/Map.bin')
        name = name.replace('data/map.bin', 'data/Map.bin')
        name = name.replace('font/', 'Font/')
        name = name.replace('graphics/background/', 'Graphics/Background/')
        name = name.replace('graphics/button/', 'Graphics/Button/')
        name = name.replace('graphics/face/', 'Graphics/Face/')
        name = name.replace('graphics/half/', 'Graphics/Half/')
        name = name.replace('graphics/mood/', 'Graphics/Mood/')
        name = name.replace('graphics/other/', 'Graphics/Other/')
        name = name.replace('graphics/system/', 'Graphics/System/')
        name = name.replace('graphics/transitions/', 'Graphics/Transitions/')
        name = name.replace('graphics/ui/', 'Graphics/UI/')
        name = name.replace('graphics/chat/', 'Graphics/Chat/')
        name = name.replace('graphics/oafs/', 'Graphics/Oafs/')
        fileName.append(name)
    for i in range(len(fileName)):
        if fileName[i] == "data/Game.bin":
            file = http.request('GET', 'http://wcdn1.cgyouxi.com/shareres/' + MD5[i][:2] + '/' + MD5[i]).data
            with open('./download/'+gindex+'.bin', 'wb') as f:
                _ = f.write(file)
            if FLAG:
                print(gindex+'_'+ver+'_ue') #.decode('unicode_escape')
            else:
                print(gindex+'_'+ver)
            break


def getIDS():
    global FLAG_I
    ids = set()
    for i in range(1,5):
        if os.path.exists('id_name_ver_desc_tags'+str(i)+'.json'):
            FLAG_I[i] -= 1
        if (not os.path.exists('id_name_ver_desc_tags'+str(i)+'.json')) or (os.path.exists('id_name_ver_desc_tags'+str(i)+'.json') and FLAG_I[i]==0):
            data = open('out_getlist'+str(i)+'.log','r',encoding='utf8').readlines()
            for line in data:
                try:
                    ids.add(int(line.split(' ')[0]))
                except:
                    continue
    return ids
    

def download(ids):
    downloaded = set([int(line.strip()) for line in open('downloaded.log','r',encoding='utf8').readlines()])
    for id in ids:
        if id in downloaded:
            continue
        try:
            get_gamebin(id)
            with open('downloaded.log','a',encoding='utf8') as f:
                _=f.write(str(id)+'\n')
        except:
            try:
                get_gamebin(id) # try again
                with open('downloaded.log','a',encoding='utf8') as f:
                    _=f.write(str(id)+'\n')
            except Exception as e: # log it if failed again
                with open("error.log", 'a', encoding='utf-8') as f:
                    #_ = f.write(str(id)+' || '+e+'\n')
                    _ = f.write(str(id)+'\n')

def download_specific(ids):
    for id in ids:
        try:
            get_gamebin(id)
            with open('downloaded.log','a',encoding='utf8') as f:
                _=f.write(str(id)+'\n')
        except:
            print('e ',id)
            #with open("error.log", 'a', encoding='utf-8') as f:
            #    _ = f.write(str(id)+'\n')

downloaded = set([int(line.strip()) for line in open('downloaded.log','r',encoding='utf8').readlines()])
ids = getIDS()
ids_s = ids.difference(downloaded)
ids_s = ids_s.difference(set([443024,1198109,559893,1362764,543679,167854,1216751,1510058, 1, 362964, 362967, 362968, 362969, 362970, 362972, 362974]))
print(len(ids_s))
download_specific(ids_s)
downloaded = set([int(line.strip()) for line in open('downloaded.log','r',encoding='utf8').readlines()])
print("Failed ID: ", ids_s.difference(downloaded))
'''
while(True):
    ids = getIDS()
    download(ids)
    if FLAG_I[1]<1 and FLAG_I[2]<1 and FLAG_I[3]<1 and FLAG_I[4]<1:
        downloaded = set([int(line.strip()) for line in open('downloaded.log','r',encoding='utf8').readlines()])
        ids = set()
        for i in range(1,5):
            data = open('out_getlist'+str(i)+'.log','r',encoding='utf8').readlines()
            for line in data:
                try:
                    ids.add(int(line.split(' ')[0]))
                except:
                    continue
        print("Failed ID: ", ids.difference(downloaded))
        exit(1)
    time.sleep(3600)
'''
