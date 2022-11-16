#https://github.com/ssz66666/66rpg-spoofer/     <-- old method
#https://github.com/PeaShooterR/fuck66rpg       <-- Thank you!
import urllib3, json, base64, re, os, gc

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
    http = urllib3.PoolManager()
    gameLink = 'https://www.66rpg.com/f/' + str(gindex) + '/ref/d3d3LjY2cnBnLmNvbQ=='
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
            print(str(gindex)+'_'+ver+'_failed')
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
            with open('./download/'+str(gindex)+'.bin', 'wb') as f:
                _ = f.write(file)
            if FLAG:
                print(str(gindex)+'_'+ver+'_ue') #.decode('unicode_escape')
            else:
                print(str(gindex)+'_'+ver)
            break

#id_name_ver_desc_tags = json.load(open('id_name_ver_desc_tags_checkpoint.json','r',encoding='utf8'))
id_name_ver_desc_tags = json.load(open('id_name_ver_desc_tags.json','r',encoding='utf8'))
ids = [int(i) for i in id_name_ver_desc_tags.keys()]
id_name_ver_desc_tags.clear()
downloaded = [int(fn[:-4]) for fn in os.listdir('./download/')]
max_down = max(downloaded)
del id_name_ver_desc_tags
del downloaded
gc.collect()
for id in ids: #range(158000):
    if id <= max_down:
        continue
    try:
        get_gamebin(id)
    except:
        try:
            get_gamebin(id) # try again
        except Exception as e: # log it if failed again
            with open("error.log", 'a', encoding='utf-8') as f:
                _ = f.write(str(id)+' || '+e+'\n')

downloaded = [int(fn[:-4]) for fn in os.listdir('./download/')]
print("Failed ID: ", set(ids).difference(set(downloaded)))
#failed: {35557, 19045, 53064, 54443, 38095, 38800, 37841, 18161, 14291, 20342, 24120, 49371, 13406}
#

'''
filePath = []  # 提出文件路径用于创建文件夹
for a in fileName:
    filepathIndex = a.rfind('/')
    filePath.append(a[:filepathIndex])

# 下载素材文件
# http://wcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$
# 网页客户端的CDN为，似乎都可以使用
# https://dlcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$
for i in range(len(fileName)):
    print(Path(gameName + '/' + fileName[i]), MD5[i])
    file = http.request('GET', 'http://wcdn1.cgyouxi.com/shareres/' + MD5[i][:2] + '/' + MD5[i]).data
    isExists = os.path.exists(Path(gameName + '/' + filePath[i]))
    if not isExists:  # 判断如果文件不存在,则创建
        os.makedirs(Path(gameName + '/' + filePath[i]))
    f = open(Path(gameName + '/' + fileName[i]), mode='wb')
    f.write(file)
    f.close()
'''

