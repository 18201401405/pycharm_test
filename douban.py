# coding=utf-8
#!/bin/bash python
#-*- coding:utf8 -*-

##################################################################################################
# fileName: SpiderDouBan.py
# Description: 从豆瓣网站爬取电影和电视剧的名称和评分
# Date: 2016-11-14
#
##################################################################################################

import requests
from pyquery import PyQuery as pq
import time
import  re
import random

class Tool(object):
    mImg = re.compile('<img.*?>| {1,7}|&nbsp;|&gt;')
    rmAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceline = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    #将多行空行删除
    removeNoneLine = re.compile('\n+')
    #替换多个空格为单个
    replaceMultiSpace = re.compile('\s+')
    def replace(self,x):
        x = re.sub(self.rmImg, " ", x)
        x = re.sub(self.rmAddr, " ", x)
        x = re.sub(self.replaceline, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        x = re.sub(self.removeNoneLine, "", x)
        x = re.sub(self.replaceMultiSpace, " ", x)
        x = x.replace('"','\'')
        return x.strip()
    #获取当前时间
    def getCurrentTime(self):
        currtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        # print type(currtime)
        return currtime

    #获取当前时间
    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))

    #获取html页面
    def getHtml(self,url,headers,servers=[]):
        if len(servers) > 0:
            proxyServer = {"https": random.choice(servers)}
            r = requests.get(url,headers=headers,proxies=proxyServer)
            # proxies =  random.choice(servers)
            # print proxies
        else:
            r = requests.get(url,headers=headers)
        page = r.text.encode(r.encoding)
        doc =  pq(page)
        return doc

    #获取json对象
    def getJson(self,url,headers, servers=[]):
        r = ''
        if len(servers) > 0:
            proxyServer = {"https": random.choice(servers)}
            r = requests.get(url, headers=headers, proxies=proxyServer)
        else:
            # print servers
            r = requests.get(url, headers=headers)
        return r.json()


class DouBanSpider(object):
    def __init__(self):
        self.header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17',
        # 'Referer':'https://movie.douban.com/tag/',
        # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie':'ll="108288"; bid=_yGw1kLNTNo; __utma=30149280.1535332890.1464068708.1465715048.1479106759.23; __utmz \
            =30149280.1464331669.3.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.4cf6=%5B%22%22 \
            %2C%22%22%2C1479106759%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=a2a1febd463aaaa2 \
            .1464068996.23.1479108002.1465717074.; __utma=223695111.1460286629.1464068996.1465715071.1479106759.23 \
            ; __utmz=223695111.1465715071.22.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_user_id \
            =67421a55-dfd2-480c-a542-5e421558fd96; viewed="26696632"; ue="zwcyok@163.com"; __utmv=30149280.5100; \
             __utmb=30149280.0.10.1479106759; __utmc=30149280; __utmb=223695111.0.10.1479106759; __utmc=223695111 \
            ; _pk_ses.100001.4cf6=*; ap=1; RT=nu=https%3A%2F%2Fmovie.douban.com%2Ftag%2F%25E7%25BE%258E%25E5%259B \
            %25BD%3Fstart%3D0%26type%3DT&cl=1479108008002&r=https%3A%2F%2Fmovie.douban.com%2Ftag%2F%25E7%25BE%258E \
            %25E5%259B%25BD%3Fstart%3D20%26type%3DT&ul=1479108008020'}
        # self.proxies = ['http://10.0.1.250:8888','http://117.169.77.211:8888']
        self.proxies = []
        self.tool = Tool()

    #获取电视剧评分信息
    def getTvInfo(self):
        f = open('/Users/zhouwenchun/douban_tv.txt','w')
        tagItems = self.tool.getJson('https://movie.douban.com/j/search_tags?type=tv',self.header,self.proxies)
        #遍历标签
        for item in tagItems['tags']:
            tag = item.encode('utf-8')
            print  tag
            page_no = 0
            while 1:
                page_start = page_no*20
                url ='https://movie.douban.com/j/search_subjects?type=tv&tag='+tag+'&sort=recommend&page_limit=20&page_start='+str(page_start)
                jsonObj = self.tool.getJson(url,self.header,self.proxies)
                subjects = jsonObj['subjects']
                if len(subjects)==0:
                    print tag, page_no
                    print '---------'
                    page_no = 0
                    break
                else:
                    for subject in subjects:
                        line = subject['title']+'\t'+subject['rate']+'\n'
                        print line
                        f.write(line.encode('utf-8'))
                    page_no +=1
        f.close()

    #获取电影的评分信息
    def getMvInfo(self):
        f = open('./douban_mv.txt','w')
        #获取tag列表
        doc = self.tool.getHtml('https://movie.douban.com/tag/',self.header,self.proxies)
        tagItems = doc('.tagCol').eq(1)('a')
        for item in tagItems.items():
            tag = item.text().encode('utf-8')
            print tag
             #根据tag获取总页数
            doc = self.tool.getHtml('https://movie.douban.com/tag/'+tag,self.header,self.proxies)
            total_page = doc('.paginator .thispage').eq(0).attr('data-total-page')
            print 'total_page:',total_page
            for x in xrange(0,int(total_page)):
                start = x * 20
                baseUrl = 'https://movie.douban.com/tag/'+tag+'?start='+str(start)+'&type=T'
                print baseUrl
                doc = self.tool.getHtml(baseUrl,self.header,self.proxies)
                # aItems = doc('td .nbg')
                # bItems = doc('div .rating_nums')
                # titleItems = []
                # rateItmes = []
                # for item in aItems.items():
                #     titleItems.append(item.attr('title').encode('utf-8'))
                # for item in bItems.items():
                #     rateItmes.append(item.text().encode('utf-8'))
                # for i in range(len(aItems)):
                #     line = titleItems[i-1]+'\t'+rateItmes[i-1]+'\n'
                #     print line
                #     f.write(line)
                aItem = doc('td .pl2')
                for item in aItem.items():
                    line = item('a').text().replace('\n','').replace(' ','').encode('utf-8')+'\t'+item('.rating_nums').text().encode('utf-8')+'\n'
                    print line
                    f.write(line)
            time.sleep(5)
        f.close()

def Test():
    url = 'https://movie.douban.com/tag/%E7%BE%8E%E5%9B%BD?start=860&type=T'
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17',
        # 'Referer':'https://movie.douban.com/tag/',
        # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie':'ll="108288"; bid=_yGw1kLNTNo; __utma=30149280.1535332890.1464068708.1465715048.1479106759.23; __utmz \
            =30149280.1464331669.3.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.4cf6=%5B%22%22 \
            %2C%22%22%2C1479106759%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=a2a1febd463aaaa2 \
            .1464068996.23.1479108002.1465717074.; __utma=223695111.1460286629.1464068996.1465715071.1479106759.23 \
            ; __utmz=223695111.1465715071.22.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_user_id \
            =67421a55-dfd2-480c-a542-5e421558fd96; viewed="26696632"; ue="zwcyok@163.com"; __utmv=30149280.5100; \
             __utmb=30149280.0.10.1479106759; __utmc=30149280; __utmb=223695111.0.10.1479106759; __utmc=223695111 \
            ; _pk_ses.100001.4cf6=*; ap=1; RT=nu=https%3A%2F%2Fmovie.douban.com%2Ftag%2F%25E7%25BE%258E%25E5%259B \
            %25BD%3Fstart%3D0%26type%3DT&cl=1479108008002&r=https%3A%2F%2Fmovie.douban.com%2Ftag%2F%25E7%25BE%258E \
            %25E5%259B%25BD%3Fstart%3D20%26type%3DT&ul=1479108008020'}

    r = requests.get(url,headers=header)
    page = r.text.encode(r.encoding)
    # print  page
    titleItems = []
    rateItmes = []
    doc =  pq(page)
    # aItems = doc('td .nbg')
    # # print type(aItems)
    # for item in aItems.items():
    #     print item.attr('title').encode('utf-8')
    #     # print type(item)
    #     titleItems.append(item.attr('title').encode('utf-8'))
    #     # print item.attr('title').encode('utf-8')
    # #     print item
    #     # print item.text.encode('utf-8')
    # bItems = doc('div .rating_nums')
    # for item in bItems.items():
    #     print item.text()
    #     rateItmes.append(item.text())
    #
    # for i in range(len(titleItems)):
    #     print titleItems[i-1]+'\t'+rateItmes[i-1]
    aItem = doc('td .pl2')
    for item in aItem.items():
        # print type(item)
        # print item.html()
        print item('a').text().replace('\n','').replace(' ','')
        print item('.rating_nums').text()
        print '-'*10

def main():
    spider = DouBanSpider()
    # spider.getTvInfo()
    spider.getMvInfo()
    # Test()

if __name__ == '__main__':
    main()