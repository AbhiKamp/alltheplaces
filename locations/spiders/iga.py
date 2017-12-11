# -*- coding: utf-8 -*-
import scrapy
import json
import re

from locations.items import GeojsonPointItem
DAYS=['Mo','Tu','We','Th','Fr','Sa','Su']

class IgaSpider(scrapy.Spider):
    name = "iga"
    allowed_domains = ["iga.com"]
    start_urls = (
        'https://www.iga.com/consumer/locator.aspx',
    )

    def phone_normalize(self, phone):
        if not phone:
            return
        r=re.search(r'\+?(\s+)*(\d{1})?(\s|\()*(\d{3})(\s+|\))*(\d{3})(\s+|-)?(\d{2})(\s+|-)?(\d{2})',phone)
        return ('('+r.group(4)+') '+r.group(6)+'-'+r.group(8)+'-'+r.group(10)) if r else phone

    def parse(self, response): #high-level list of states
        next_page=response.xpath('//li[@class="next"]/a/@href').extract_first()
        stores=response.xpath('//ol[contains(@class,"results")]/li')
        for store in stores:
            position=re.search(r'\?daddr=(.*),(.*)',store.xpath('.//a[contains(.,"Driving Directions")]/@href').extract_first())
            phone=store.xpath('.//span[contains(@class,"tel")]/text()').extract_first()
            if phone:
                phone=phone.replace('- Main','').strip()

            yield GeojsonPointItem(
                lat=float(position[1]),
                lon=float(position[2]),
                phone=self.phone_normalize(phone),
                website=store.xpath('.//a[contains(.,"View Our Website")]/@href').extract_first(),
                ref=store.xpath('.//div[contains(@class,"org")]/text()').extract_first(),
                opening_hours='',
                addr_full=store.xpath('.//div[contains(@class,"street-address")]/text()').extract_first(),
                city=store.xpath('.//span[contains(@class,"locality")]/text()').extract_first().rstrip(','),
                state=store.xpath('.//span[contains(@class,"region")]/text()').extract_first().strip(),
                postcode=store.xpath('.//span[contains(@class,"postal-code")]/text()').extract_first().strip(),
                country='USA',
            ) 
        if next_page:
            yield scrapy.Request(response.urljoin(next_page),callback=self.parse)
