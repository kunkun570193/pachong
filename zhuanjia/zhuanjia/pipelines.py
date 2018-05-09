# coding=utf-8
import json,redis ,logging,random,time,os
import pandas as pd
from scrapy.exceptions import DropItem
from scrapy import signals
from pybloom_live import BloomFilter
from scrapy.mail import MailSender
from jinja2 import Template
logger = logging.getLogger(__name__)


redis_db = redis.Redis(host="127.0.0.1", port=6379, db=4, password="")
redis_data_dict = "f_url"
class ZhuanjiaPipeline(object):

    def process_item(self, item, spider):
        with open("zhuanjia2.txt","a",encoding="utf-8") as f:
            f.write(json.dumps(item,ensure_ascii=False,indent=2))
            print("保存成功")

        return item

class BloomCheckPipeline(object):
    def __int__(self):
        file_name = 'bloomfilter'


    def open_spider(self, spider):
        file_name = 'bloomfilter'
        is_exist = os.path.exists(file_name + '.blm')
        self.file = dict()
        if is_exist:
            self.bf = BloomFilter.fromfile(open('bloomfilter.blm', 'rb'))
            print('open blm file success')
        else:
            self.bf = BloomFilter(100000, 0.001)
            print('didn\'t find the blm file')

    def process_item(self, item, spider):
        # 我是过滤掉相同title的item 各位看需求

        content = []
        if item["title"] not in self.bf:
            content.append(item["title"] )

            print("append title success")

        if item['href'] in self.bf:
            print('drop one item for exist')

            raise DropItem('drop an item for exist')
        else:
            self.bf.add(item['href'])

            print("add one success")
            content.append(item["href"])

            settings = spider.crawler.settings
            # body="数据更新啦，大家回来看啊"
            # body = """"
            #            <ul>
            #            {% for title, href in a[] %}
            #                <h2>{{ title }}已更新</h2>
            #
            #                    <a href="{{href }}" title="{{ title }}">{{ title }}</a>
            #                    <br>
            #                    <p>点击无跳转, 请复制此链接到浏览器<br>{{ url }}</p>
            #                    <br>
            #
            #                <span>-------------------------------我是分割符--------------------------------------</span>
            #            {% endfor %}
            #            </ul>
            #            """
            # body = Template(body)
            body = content
            subject = '请查收新的数据!'  # 主题
            m = MailSender.from_settings(settings)
            m.send(to=settings.get("MAIL_TOS").get('王昱锟'), subject=subject,
                   body=str(body), mimetype='text/HTML')
            # cc=settings.get("MAIL_TOS").values(),这个是抄送的

            return item

    def close_spider(self, spider):
        self.bf.tofile(open('bloomfilter.blm', 'wb'))