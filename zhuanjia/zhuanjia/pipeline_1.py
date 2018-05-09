# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, redis, re, time, random, logging
from bspider.db import *
from bspider.items import *
from scrapy import signals
from scrapy.mail import MailSender
from jinja2 import Template

logger = logging.getLogger(__name__)


class BspiderPipeline(object):
    def __init__(self,stats):
        self.stats = stats
    @classmethod
    def from_crawler(cls, crawler):

        return cls(crawler.stats)

    def open_spider(self, spider):
        poll = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.r = redis.Redis(connection_pool=poll)
        self.file = dict()
        Base.metadata.create_all(engine)

    def _comment_item_data(self, item):  # todo 线上未变表结构
        """深度题材内参文章数据存储"""

        c = CaiData()
        c.article_id = item["article_id"]  # 以此为id
        c.title = item["title"]
        c.source = item["source"]
        c.types = int(item["types"])
        try:
            # 股票信息这些没有
            c.published_time = item["published_time"]
            c.reads = int(item["reads"])
            c.body = item["body"]
        except KeyError as e:
            logger.info('股票信息')

        session.merge(c)
        session.commit()

    def _ctock_item_data(self, item):
        """内参涨停板数据存储"""
        z = ZhData()
        z.types = int(item["types"])
        z.name = item["name"]
        z.code = item["code"]
        z.times = item['times']
        z.v_num = int(item["v_num"])
        z.version = item["version"]
        z.reason = item["reason"]
        z.strength = item["strength"]
        z.article_id = item["article_id"]
        try:
            session.add(z)
            session.commit()
        except Exception as e:
            logger.error(e)

    def _b_item_data(self, item):
        """币世界数据存储"""
        img_0 = item.get("img_0", None)
        if img_0 is None:
            name = item.get("name", None)
            mate = json.dumps(item)
            self.r.set(f"platform_{name}", mate, ex=3600)
            return item
        mate = json.dumps({"data": item})
        self.r.set(f"{img_0}", mate, ex=3600)

    def _zhongitem_data(self, item):
        """中金博客历史数据存储"""
        z = ZhongData()
        z.title = item["title"]
        z.time = item["time"]
        z.reads = item["reads"]
        z.con = item["con"]
        z.author = item["author"]
        z.ids = item["ids"]
        try:
            session.merge(z)
            session.commit()
        except Exception as e:
            logger.error(e)

    def _zhongjinitem_data(self, item, spider):
        """中金博客数据变更处理"""
        author = item.get("author")
        xin_data = item['url']  # 新数据
        url_title = item.get("url_title")
        old_data = self.r.get(author)  # 取数据
        mate = json.dumps({"data": xin_data})
        if old_data is None:  # 最初 没有数据
            self.r.set(author, mate)

        # # todo 测试专用
        random_num = random.randint(100, 999)
        random_url = f"http://blog.cnfol.com/QQ320907778/article/134378{random_num}.html"
        random_url1 = f"http://blog.cnfol.com/QQ320907778/article/134388{random_num}.html"
        xin_data.append(random_url)
        url_title.append((random_url,'ssssss'))
        xin_data.append(random_url1)
        url_title.append((random_url1,'wwww'))

        old_data = json.loads(old_data)   # todo 更新测试 2018-04-24 11:29:18
        url = list(set(xin_data).difference(set(old_data.get("data"))))  # 本次结果与上次结果对比取出更新的url
        if len(url):
            url_ = [i for i in url_title if i[0] in url]
            self.file[author] = url_
            self.r.set(author, mate)
        # flag = self.r.set(author, mate)
        # if flag:
        #     """更新"""
        #     set_dict = json.loads(set_flag.pop())
        #     set_list = set_dict.get('data')  # 取出上次执行结果
        #     # todo 2018-04-24 10:55:59 执行一次
        #     url = list(set(url_title).difference(set(set_list)))  # 本次结果与上次结果对比取出更新的url
        #     self.file[author] = url

    def process_item(self, item, spider):
        if isinstance(item, CommentItem):  # 财联社深度题材文章
            self._comment_item_data(item)
        elif isinstance(item, CtockItem):  # 财联社股票数据
            self._ctock_item_data(item)
        elif isinstance(item, BspiderItem):  # 币世界行情
            self._b_item_data(item)
        elif isinstance(item, ZhongItem):  # 中金博客历史数据
            self._zhongitem_data(item)
        elif isinstance(item, ZhongJindata):  # 中金博客更新
            self._zhongjinitem_data(item, spider)
        elif isinstance(item, BtitleItem):  # 币世界行情顶部
            flag = item['flag']
            mate = json.dumps(item)
            self.r.set(f"top_{flag}", mate)
        elif isinstance(item, Jin10Item):
            print("*"*60)
        return item

    def close_spider(self, spider):
        """爬虫关闭"""
        stats_dict = self.stats.get_stats()  # 爬虫收集器
        if spider.name == 'zz' and len(self.file):
            settings = spider.crawler.settings
            subject = f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}请查收!'  # 主题
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
            m = MailSender.from_settings(settings)
            m.send(to=settings.get("MAIL_TOS").get('小花'), cc=settings.get("MAIL_TOS").values(), subject=subject,
                   body=body.render(file=self.file), mimetype='text/HTML')


    # @classmethod
    # def from_crawler(cls, crawler):
    #     """绑定信号"""
    #     pipeline = cls()
    #     crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    #     crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    #     return pipeline
    #
    # def spider_closed(self, spider):  # todo 扩展到每个爬虫结束报告通知
    #     """爬虫关闭发送变化的url"""
    #
    # def spider_opened(self, spider):
    #     logger.info('爬虫开始')
    #     """爬虫打开建立一个容器存储变化的url"""

