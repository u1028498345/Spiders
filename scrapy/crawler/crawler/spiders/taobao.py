# -*- coding: utf-8 -*-
import re

from scrapy import Spider
from scrapy import Request
from utils import extract_one,extract
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from crawler.items import Good

class TBSpider(Spider):
    name='tb'
    allowed_domains=['taobao.com']
    start_urls=['https://top.taobao.com/index.php?topId=TR_FS&leafId=50010850','https://top.taobao.com/index.php?topId=TR_SM&leafId=1101','https://top.taobao.com/index.php?topId=TR_HZP&leafId=121454013','https://top.taobao.com/index.php?topId=TR_MY&leafId=50013618','https://top.taobao.com/index.php?topId=TR_SP&leafId=50008055','https://top.taobao.com/index.php?topId=TR_WT&leafId=50014075','https://top.taobao.com/index.php?topId=TR_JJ&leafId=50016434','https://top.taobao.com/index.php?topId=TR_ZH&leafId=50011975']
    url_pattern=[r'.*rank=sale&type=hot.*']
    url_extractor=LxmlLinkExtractor(allow=url_pattern)
    item_dict={}

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url,callback=self.parse,args={
                'wait':5.5,'html':1,
            }
            )

    def parse(self,response):
        hxs=Selector(response,type="html")
        item_url_list=extract(hxs,"//div[@class='block-body ']/div[@class='params-cont']/a/@href")
#        //div[@class='block-body ']/div[@class='params-cont']/a/@href
        for url in item_url_list:
            url=url.replace('./index.php?','https://top.taobao.com/index.php?')
            yield SplashRequest(url,callback=self.extract_url,args={'wait':5.5,'html':1})

    def extract_url(self,response):
        hxs=Selector(response,type="html")
        for link in self.url_extractor.extract_links(response):
            yield SplashRequest(link.url,callback=self.parse_item,args={'wait':5.5,'html':1})

    def parse_item(self,response):
        print response.url
        hxs=Selector(response)
        #https://top.taobao.com/index.php?leafId=50015380&rank=sale&topId=TR_ZH&type=hot
        top_id=re.findall(r'.*&topId=(\S+_\S+)&type.*',response.url)[0]
        type_id=re.findall(r'.*leafId=(\d+)&rank=.*',response.url)[0]
        ranks_tuple=extract(hxs,'//*[@class="rank-num rank-focus"]/text()|//*[@class="rank-num rank-important"]/text()|//*[@class="rank-num rank-"]/text()')
        ranks=[]
        for r in ranks_tuple:
            if r.strip()!='':
                ranks.append(r)

        titles=extract(hxs,'//*[@class="title"]/a/text()')
        prices=extract(hxs,'//*[@class="col3 col"]/text()')[1:]
        turnover_indexs=extract(hxs,'//*[@class="focus-bar"]/span/text()')

        for r,t,p,i in zip(ranks,titles,prices,turnover_indexs):
            good={
                'mall':'0',
                'rank':r.strip(),
                'title':t.strip(),
                'price':p.split('￥')[-1].strip(),
                'turnover_index':i.strip(),
                'top_id':top_id.strip(),
                'type_id':type_id.strip(),
                'url':response.url
            }
            yield Good(good)
