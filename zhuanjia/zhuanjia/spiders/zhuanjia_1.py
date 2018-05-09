# -*- coding: utf-8 -*-
import scrapy, json
from copy import deepcopy
import re
from zhuanjia.items import ZhuanjiaItem


class Zhuanjia1Spider(scrapy.Spider):
    name = 'zhuanjia_1'
    allowed_domains = ['blog.cnfol.com']
    start_urls = ['http://blog.cnfol.com/QQ320907778/articlelist/alist']

    def parse(self, response):
        li_list = response.xpath("//div[@class='MaLft']//dd/ul/li")

        for li in li_list:

            item = {}
            item["title"] = li.xpath("./h4/a/text()").extract_first()
            item["href"] = li.xpath("./h4/a/@href").extract_first()
            item["time"] = li.xpath("./span/text()").extract_first()

            # if item["href"] is not None:
            #     yield scrapy.Request(
            #         item["href"], meta={"item": item}, callback=self.parse
            #     )
            yield item

        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        if next_url is not None:
            next_url = next_url
            yield scrapy.Request(
                next_url, callback=self.parse
            )

    # def parse_detail(self, response):
    #     item = deepcopy(response.meta["item"])
    #     item["content"] = response.xpath("//div[@class='MaLft']//span").xpath('string(.)').extract()
    #     if item["content"]:
    #         item["content"] = [re.sub('\t', '', i) for i in item["content"]]
    #         item["content"] = [re.sub('\n', '', i) for i in item["content"]]
    #         item["content"] = [re.sub('\r', '', i) for i in item["content"]]
    #         item["content"] = [re.sub(' ', '', i) for i in item["content"]]
    #     else:
    #         item["content"] = None
    #
    #     img = response.xpath("//div[@class='MaLft']//span/img/@src").extract()
    #     item["img"] = img

        # yield item
