# -*- coding: utf-8 -*-
from BiliClient import VideoUploader
from getopt import getopt
import os, json, sys, re, time

def main(*args, **kwargs):
    try:
        if os.path.exists('./config/config.json'):
            with open('./config/config.json','r',encoding='utf-8') as fp:
                configData: dict = json.loads(re.sub(r'\/\*[\s\S]*?\*\/', '', fp.read()))
        elif os.path.exists('/etc/BiliExp/config.json'):
            with open('/etc/BiliExp/config.json','r',encoding='utf-8') as fp:
                configData: dict = json.loads(re.sub(r'\/\*[\s\S]*?\*\/', '', fp.read()))
        else:
            raise FileNotFoundError('未找到账户配置文件')
    except Exception as e: 
        print(f'配置加载异常，原因为{str(e)}，退出程序')
        sys.exit(6)

    if not kwargs["path"]:
        raise ValueError('未提供视频文件路径')
    if not os.path.exists(kwargs["path"]):
        raise FileNotFoundError(kwargs["path"])
    if kwargs["cover"] and not os.path.exists(kwargs["cover"]):
        raise FileNotFoundError(kwargs["cover"])

    video_uploader = VideoUploader(configData["users"][0]["cookieDatas"])
    video_uploader.setTid(kwargs["tid"])
    if kwargs["title"]:
        video_uploader.setTitle(kwargs["title"])
    if kwargs["desc"]:
        video_uploader.setDesc(kwargs["title"])
    if kwargs["nonOriginal"]:
        video_uploader.setCopyright(2)
    else:
        video_uploader.setCopyright(1)
    if kwargs["source"]:
        video_uploader.setSource(kwargs["source"])
    if kwargs["dtime"]:
        video_uploader.setDtime(kwargs["dtime"])

    print('正在上传中.....')
    if kwargs["singleThread"]:
        video_info = video_uploader.uploadFileOneThread(kwargs["path"])
    else:
        video_info = video_uploader.uploadFile(kwargs["path"])
    
    if not video_info:
        print('上传失败')
        exit()

    video_uploader.add(video_info)

    if kwargs["cover"]:
        video_uploader.setCover(kwargs["cover"])
    else:
        print('未设置封面，等待官方生成封面...')
        i = 12
        pics = []
        while i:
            time.sleep(10) #B站需要足够的时间来生成封面
            try:
                pics = video_uploader.recovers(video_info) #获取视频截图，刚上传的视频可能获取不到
            except:
                ...
            if pics:
                video_uploader.setCover(pics[0]) #设置视频封面
                break
            i -= 1

    if kwargs["tags"]:
        video_uploader.setTag(kwargs["tags"])
    else:
        video_uploader.setTag(video_uploader.getTags(video_info)[0:1])

    result = video_uploader.submit()
    if 'bvid' in result:
        print(f'提交成功，av{result["aid"]}，{result["bvid"]}')
    else:
        print(f'提交失败,原因为{result["message"]}')

if __name__=="__main__":
    kwargs = {
        "path": None,
        "title": None,
        "desc": None,
        "cover": None,
        "tid": 174,
        "tags": None,
        "nonOriginal": False,
        "source": None,
        "singleThread": False,
        "dtime": 0
        }
    opts, args = getopt(sys.argv[1:], "hVnSv:t:d:c:i:T:s:D:", ["help", "version", "nonOriginal", "singleThread", "videopath=", "title=", "desc=", "cover=", "tid=", "tags=", "source=", "DelayTime="])
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('VideoUploader -v <视频文件路径> -t <视频标题> -d <视频简介> -c <视频封面图片路径> -t <视频标签> -n -s <非原创时视频来源网址>')
            print(' -v --videopath     视频文件路径')
            print(' -t --title         视频标题，不指定默认为视频文件名')
            print(' -d --desc          视频简介，不指定默认为空')
            print(' -c --cover         视频封面图片路径，不提供默认用官方提供的第一张图片')
            print(' -i --tid           分区id，默认为174，即生活,其他分区')
            print(' -T --tags          视频标签，多个标签用半角逗号隔开，带空格必须打引号，不提供默认用官方推荐的前两个标签')
            print(' -n --nonOriginal   勾选转载，不指定本项默认为原创')
            print(' -s --source        -n参数存在时指定转载源视频网址')
            print(' -D --DelayTime     发布时间戳,10位整数,官方的延迟发布,时间戳距离现在必须大于4小时')
            print(' -S --singleThread  单线程上传,如果出现上传失败时使用,不指定本项为3线程上传')
            print(' -V --version       显示版本信息')
            print(' -h --help          显示帮助信息')
            print('以上参数中只有-v --videopath为必选参数，其他均为可选参数')
            exit()
        elif opt in ('-V','--version'):
            print('B站视频上传器 videoDownloader v1.1.8')
            exit()
        elif opt in ('-v','--videopath'):
            kwargs["path"] = arg.replace(r'\\', '/')
        elif opt in ('-t','--title'):
            kwargs["title"] = arg
        elif opt in ('-d','--desc'):
            kwargs["desc"] = arg
        elif opt in ('-c','--cover'):
            kwargs["cover"] = arg
        elif opt in ('-i','--tid'):
            kwargs["tid"] = int(arg)
        elif opt in ('-T','--tags'):
            kwargs["tags"] = list(arg.split(','))
        elif opt in ('-n','--nonOriginal'):
            kwargs["nonOriginal"] = True
        elif opt in ('-s','--source'):
            kwargs["source"] = arg
        elif opt in ('-S','--singleThread'):
            kwargs["singleThread"] = True
        elif opt in ('-D','--DelayTime'):
            kwargs["dtime"] = int(arg)
    main(**kwargs)