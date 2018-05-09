# coding: utf-8

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json,redis ,logging,random,time,os
import pandas as pd
from scrapy.exceptions import DropItem
from scrapy import signals
from pybloom_live import BloomFilter
from scrapy.mail import MailSender
from jinja2 import Template
logger = logging.getLogger(__name__)


redis_db = redis.Redis(host="127.0.0.1", port=6379, db=4, password="")
# redis_data_dict = "f_url"


from zhuanjia.items import ZhuanjiaItem

class ZhuanjiaPipeline(object):

    def process_item(self, item, spider):
        with open("zhuanjia2.txt","a",encoding="utf-8") as f:
            f.write(json.dumps(item,ensure_ascii=False,indent=2))
            print("保存成功")

        return item


# class DuplicatePipeline(object):
    """"
    去重redis

    """
    # def __init__(self):
    #     if redis_db.hlen(redis_data_dict) == 0:
    #         sql = "SELECT uuid FROM f_data"
    #         df = pd.read_sql(sql, con="mysql+pymysql://root:xin123456@127.0.0.1/bw_admin?charset=utf8")
    #         for uuid in df["uuid"].get_value():
    #             redis_db.hset(redis_data_dict, uuid, 0)
    #
    # def process_item(self, item, spider):
    #     if redis_db.hexists(redis_data_dict, item["uuid"]):
    #         raise DropItem("Duplicate item found:%s" % item)
    #     return item

class BloomCheckPipeline(object):
    def __int__(self):
        file_name = 'bloomfilter'

    def open_spider(self, spider):
        file_name = 'bloomfilter'
        is_exist = os.path.exists(file_name + '.blm')
        if is_exist:
            self.bf = BloomFilter.fromfile(open('bloomfilter.blm', 'rb'))
            print('open blm file success')
        else:
            self.bf = BloomFilter(100000, 0.001)
            print('didn\'t find the blm file')
        self.file=dict()
        self.r=redis_db

    def old_data(self,item):  #专家历史数据
        z=_zhuanjia_data()
        z.author = item["author"]
        try:
            session.merge(z)
            session.commit()
        except Exception as e:
            logger.error(e)
    def zhuanjia_data(self,item,spider):
        """处理专家变更数据"""
        author = item.get("author")
        xin_data=item['url'] #新数据
        url_title=item.get("url_title")
        old_data = self.r.get(author)  # 取数据
        mate=json.dumps(({"data":xin_data}))
        if old_data is None:# 最初 没有数据
            self.r.set(author,mate)

        random_num = random.randint(100, 999)
        random_url ="http://blog.cnfol.com/QQ320907778/article/134378{random_num}.html"
        random_url1 ="http://blog.cnfol.com/QQ320907778/article/134388{random_num}.html"
        xin_data.append(random_url)
        url_title.append((random_url, 'ssssss'))
        xin_data.append(random_url1)
        url_title.append((random_url1, 'wwww'))

        old_data=json.loads(old_data)
        url=list(set(xin_data).difference(set(old_data.get("data")))) #本次结果与上次结果对比取出更新的url
        if len(url):
            url_=[i for i in url_title if i[0] in url]
            self.file[author]=url_
            self.r.set(author,mate)


    def process_item(self, item, spider):
        #我是过滤掉相同title的item 各位看需求
        if item['url_list'] in self.bf:
            print('drop one item for exist')

            raise DropItem('drop an item for exist')
        else:
            self.bf.add(item['url_list'])

            print("add one success")
            # stats_dict = self.stats.get_stats()  # 爬虫收集器
            if spider.name == 'zhuanjia_1' and len(self.file):
                # settings = spider.crawler.settings
                # subject = '{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}请查收!'  # 主题
                body = """"
                       <ul>
                       {% for author, url_ in file.items() %}
                           <h2>{{ author }}已更新</h2>
                           {% for url,title in url_ %}
                               <a href="{{ url }}" title="{{ title }}">{{ title }}</a>
                               <br>
                               <p>点击无跳转, 请复制此链接到浏览器<br>{{ url }}</p>
                               <br>
                           {% endfor %}
                           <span>-------------------------------我是分割符--------------------------------------</span>
                       {% endfor %}
                       </ul>
                       """
            body = Template(body)

            settings = spider.crawler.settings
            subject = '{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}请查收!'
            # subject="Python SMTP 邮件测试"

            m = MailSender.from_settings(settings)
            m.send(to=settings.get("MAIL_TOS").get('王昱锟'),  subject=subject,
                   body=body.render(file=self.file), mimetype='text/HTML')
            #cc=settings.get("MAIL_TOS").values(),这个是抄送的

            return item


    def close_spider(self, spider):
        self.bf.tofile(open('bloomfilter.blm', 'wb'))






















