#!/usr/bin/env python
#
# autor: Ethan Liu
#
# description...
#

import sys
# import argparse
# import json
import os
import glob
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from scrapy.item import Item, Field
from urllib.parse import urlparse

_REPO_URL = "https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/index.html"
# _REPO_URL = "http://localhost/moe/index.html"

_DOWNLOAD_DIR = ""

class MoeSpider(Spider):
    name = 'moe'
    start_urls = [_REPO_URL]

    def __init__(self, *args, **kwargs):
        super(MoeSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # Extract URLs from the index page
        for link in response.css('a'):
            link_text = link.css('::text').get()
            link_url = link.css('::attr(href)').get()
            if link_text and self.is_content_url(link_text, link_url):
                # print(f"link: {link_url}")
                yield Request(
                    url=response.urljoin(link_url),
                    callback=self.parse_content_page
                )

    def parse_content_page(self, response):
        links = response.xpath('//text()[contains(., "文字資料庫")]/following::a[1]/@href').getall()
        # print(links)
        for link in links:
            full_url = response.urljoin(link)
            yield Request(
                url=full_url,
                callback=self.download_file,
                meta={'source_url': response.url}
            )

    def is_content_url(self, link_text, link_url):
        # exclude dcit_mini
        if 'dict_mini' in link_url:
            return False
        return '資料下載' in link_text.lower()

    # def is_file_url(self, url):
    #     return url.endswith(('.pdf', '.doc', '.docx', '.txt'))

    def download_file(self, response):
        global _DOWNLOAD_DIR
        # self.download_folder = _DOWNLOAD_DIR

        if not os.path.exists(_DOWNLOAD_DIR):
            os.makedirs(_DOWNLOAD_DIR)

        file_url = response.url
        # source_url = response.meta['source_url']

        # Generate a filename from the URL
        file_name = os.path.basename(urlparse(file_url).path)
        file_path = os.path.join(_DOWNLOAD_DIR, file_name)

        if os.path.exists(file_path):
            # self.logger.info(f"File exists: {file_path}")
            print(f"[exists] {file_path}")
            return

        try:
            with open(file_path, 'wb') as f:
                f.write(response.body)
            # self.logger.info(f"Downloaded: {file_path}")
            print(f"[new] {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to download {file_url}: {str(e)}")
            # print(f"Failed to download {file_url}: {str(e)}")

def run_spider():
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'MEMUSAGE_ENABLED': False,
        'LOG_LEVEL': 'ERROR',  # Set to 'DEBUG' for more detailed logs
        'CONCURRENT_REQUESTS': 1,  # Adjust based on your needs and server limitations
        'DOWNLOAD_DELAY': 1,  # Add a delay between requests to be polite
        # 'ITEM_PIPELINES': {'__main__.PrintPipeline': 300},
    })

    process = CrawlerProcess(settings)
    process.crawl(MoeSpider)
    process.start()

def archive(prefix: str):
    global _DOWNLOAD_DIR
    paths = glob.glob(f"{_DOWNLOAD_DIR}/{prefix}_*")
    sorted_paths = sorted(paths, key=os.path.getmtime)
    sorted_paths.pop()
    # print(sorted_paths)
    result = False
    if len(sorted_paths) > 1:
        result = True
    for path in sorted_paths:
        # print(f"Delete {path}")
        os.remove(path)
    return result

def main():
    global _DOWNLOAD_DIR
    _DOWNLOAD_DIR = sys.argv[1]

    # run_spider()
    archive("dict_concised")
    archive("dict_idioms")
    # archive("dict_mini")
    archive("dict_revised")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt by user")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    # except BaseException as err: