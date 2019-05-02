import scrapy


class HpscaSpider(scrapy.Spider):
    name = "HpscaSpider"
    start_urls = ['http://isystems.hpcsa.co.za/iregister/PractitionerView.aspx?FILENO=997034557']

    def parse(self, response):
        pass
