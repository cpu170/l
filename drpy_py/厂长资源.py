# coding=utf-8
# !/usr/bin/python
import sys

sys.path.append('..')
try:
    # from base.spider import Spider as BaseSpider
    from base.spider import BaseSpider
except ImportError:
    from t4.base.spider import BaseSpider
import base64
import hashlib
import requests
from Crypto.Cipher import AES
import urllib
# import re
import json


# from base.htmlParser import jsoup

class Spider(BaseSpider):  # 元类 默认的元类 type
    def getName(self):
        return "厂长资源"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "国产剧": "gcj",
            "最新电影": "zuixindianying",
            "电视剧": "dsj",
            "美剧": "meijutt",
            "韩剧": "hanjutv",
            "番剧": "fanju",
            "动漫": "dm",
            "豆瓣电影Top250": "dbtop250"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        url = "https://www.czys.pro"
        header = {
            "Connection": "keep-alive",
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
        rsp = self.getCookie(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//div[contains(@class,'leibox')]//ul/li")
        videos = []
        for a in aList:
            name = a.xpath('./a/img/@alt')[0]
            pic = a.xpath('./a/img/@data-original')[0]
            mark = ''.join(a.xpath(".//*[@class='hdinfo']//span/text()"))
            sid = a.xpath("./a/@href")[0]
            sid = self.regStr(sid, "/movie/(\\S+).html")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result

    def getCookie(self, url):
        header = {
            "Referer": 'https://www.czys.pro/',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
        session = requests.session()
        rsp = session.get(url)
        if '人机验证' in rsp.text:
            append = self.regStr(rsp.text, 'src=\"(/.*?)\"')
            nurl = 'https://www.czys.pro' + append
            nrsp = session.get(nurl, headers=header)
            key = self.regStr(nrsp.text, 'var key=\"(.*?)\"')
            avalue = self.regStr(nrsp.text, 'value=\"(.*?)\"')
            c = ''
            for i in range(0, len(avalue)):
                a = avalue[i]
                b = ord(a)
                c = c + str(b)
            value = hashlib.md5(c.encode()).hexdigest()
            session.get(
                'https://www.czys.pro/a20be899_96a6_40b2_88ba_32f1f75f1552_yanzheng_ip.php?type=96c4e20a0e951f471d32dae103e83881&key={0}&value={1}'.format(
                    key, value), headers=header)
            return session.get(url, headers=header)
        elif '检测中' in rsp.text:
            append = self.regStr(rsp.text, 'href =\"(/.*?)\"')
            session.get('https://www.czys.pro{0}'.format(append), headers=header)
            return session.get(url, headers=header)
        else:
            return rsp

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = 'https://www.czys.pro/{0}/page/{1}'.format(tid, pg)
        rsp = self.getCookie(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//div[contains(@class,'bt_img mi_ne_kd mrb')]/ul/li")
        videos = []
        for a in aList:
            name = a.xpath('./a/img/@alt')[0]
            pic = a.xpath('./a/img/@data-original')[0]
            mark = ''.join(a.xpath(".//div[@class='jidi']//span/text()"))
            if not mark:
                mark = ''.join(a.xpath("./div[@class='hdinfo']//span/text()"))
            sid = a.xpath("./a/@href")[0]
            sid = self.regStr(sid, "/movie/(\\S+).html")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.czys.pro/movie/{0}.html'.format(tid)
        rsp = self.getCookie(url)
        root = self.html(self.cleanText(rsp.text))
        node = root.xpath("//div[@class='dyxingq']")[0]
        pic = node.xpath(".//div[@class='dyimg fl']/img/@src")[0]
        title = node.xpath('.//h1/text()')[0]
        detail = root.xpath(".//div[@class='yp_context']//p/text()")[0]
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": detail
        }
        infoArray = node.xpath(".//ul[@class='moviedteail_list']/li")
        for info in infoArray:
            content = info.xpath('string(.)')
            if content.startswith('地区'):
                tpyeare = ''
                for inf in info:
                    tn = inf.text
                    tpyeare = tpyeare + '/' + '{0}'.format(tn)
                    vod['vod_area'] = tpyeare.strip('/')
            if content.startswith('年份'):
                vod['vod_year'] = content.replace("年份：", "")
            if content.startswith('主演'):
                tpyeact = ''
                for inf in info:
                    tn = inf.text
                    tpyeact = tpyeact + '/' + '{0}'.format(tn)
                    vod['vod_actor'] = tpyeact.strip('/')
            if content.startswith('导演'):
                tpyedire = ''
                for inf in info:
                    tn = inf.text
                    tpyedire = tpyedire + '/' + '{0}'.format(tn)
                    vod['vod_director'] = tpyedire.strip('/')
        vod_play_from = '$$$'
        playFrom = ['厂长']
        vod_play_from = vod_play_from.join(playFrom)
        vod_play_url = '$$$'
        playList = []
        vodList = root.xpath("//div[@class='paly_list_btn']")
        for vl in vodList:
            vodItems = []
            aList = vl.xpath('./a')
            for tA in aList:
                href = tA.xpath('./@href')[0]
                name = tA.xpath('./text()')[0].replace('\xa0', '')
                tId = self.regStr(href, '/v_play/(\\S+).html')
                vodItems.append(name + "$" + tId)
            joinStr = '#'
            joinStr = joinStr.join(vodItems)
            playList.append(joinStr)
        vod_play_url = vod_play_url.join(playList)

        vod['vod_play_from'] = vod_play_from
        vod['vod_play_url'] = vod_play_url
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, wd, quick=False, pg=1):
        url = 'https://www.czys.pro/daoyongjiekoshibushiyoubing?q={0}'.format(urllib.parse.quote(wd))
        rsp = self.getCookie(url)
        root = self.html(self.cleanText(rsp.text))
        vodList = root.xpath("//div[contains(@class,'mi_ne_kd')]/ul/li/a")
        videos = []
        for vod in vodList:
            name = vod.xpath('./img/@alt')[0]
            pic = vod.xpath('./img/@data-original')[0]
            href = vod.xpath('./@href')[0]
            tid = self.regStr(href, 'movie/(\\S+).html')
            res = vod.xpath('./div[@class="jidi"]/span/text()')
            if len(res) == 0:
                remark = '全1集'
            else:
                remark = vod.xpath('./div[@class="jidi"]/span/text()')[0]
            videos.append({
                "vod_id": tid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        result = {
            'list': videos
        }
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {
        "Referer": "https://www.czys.pro/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }

    def parseCBC(self, enc, key, iv):
        keyBytes = key.encode("utf-8")
        ivBytes = iv.encode("utf-8")
        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)
        msg = cipher.decrypt(enc)
        paddingLen = msg[len(msg) - 1]
        return msg[0:-paddingLen]

    def playerContent(self, flag, id, vipFlags):
        result = {}
        url = 'https://www.czys.pro/v_play/{0}.html'.format(id)
        rsp = self.getCookie(url)
        pat = '\\"([^\\"]+)\\";var [\\d\\w]+=function dncry.*md5.enc.Utf8.parse\\(\\"([\\d\\w]+)\\".*md5.enc.Utf8.parse\\(([\\d]+)\\)'
        html = rsp.text
        print(html)
        content = self.regStr(html, pat)
        if content == '':
            url = self.regStr(reg='<iframe.*?src=\"(.*?)\".*?</iframe>', src=html)
            config = self.fetch(url).text
            # jsp=jsoup()
            # url=jsp.pdfh(html, "body&&iframe&&src")
            # self.log(url)
            # config=jsp.pdfh(self.fetch(url).text,'body&&script&&Html')
            # self.log(config)
            player = self.regStr(reg='var rand = \"(.*?)\".*var player = \"(.*?)\"', src=config.replace('\n', ''),
                                 group=2)
            rand = self.regStr(reg='var rand = \"(.*?)\".*var player = \"(.*?)\"', src=config.replace('\n', ''),
                               group=1)
            decontent = self.parseCBC(base64.b64decode(player), 'VFBTzdujpR9FWBhe', rand).decode()
            str3 = json.loads(decontent)['url']
            pars = 0
            header = ''
        else:
            key = self.regStr(html, pat, 2)
            iv = self.regStr(html, pat, 3)
            decontent = self.parseCBC(base64.b64decode(content), key, iv).decode()
            urlPat = 'video: \\{url: \\\"([^\\\"]+)\\\"'
            vttPat = 'subtitle: \\{url:\\\"([^\\\"]+\\.vtt)\\\"'
            str3 = self.regStr(decontent, urlPat)
            str4 = self.regStr(decontent, vttPat)
            self.loadVtt(str3)
            pars = 0
            header = ''
            if len(str4) > 0:
                result['subf'] = '/vtt/utf-8'
                result['subt'] = ''
        result = {
            'parse': pars,
            'playUrl': '',
            'url': str3,
            'header': header
        }
        return result

    def loadVtt(self, url):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {}
        return [200, "video/MP2T", action, ""]
