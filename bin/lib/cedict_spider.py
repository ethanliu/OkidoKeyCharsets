#!/usr/bin/env python
#
# autor: Ethan Liu
#
# cc-cedict spider
#
# https://www.mdbg.net/chinese/dictionary?page=cc-cedict
# https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip


import os
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from scrapy.item import Item, Field
from urllib.parse import urlparse
from lib.util import read_file, write_file

class CedictSpider(Spider):
    name = 'cedict'
    start_urls = ['https://www.mdbg.net/chinese/dictionary?page=cc-cedict']
    # start_urls = ['http://localhost/tmp/cedict.html']
    base_url = 'https://www.mdbg.net/chinese'
    download_dir = ''

    def __init__(self, download_dir = None, *args, **kwargs):
        super(CedictSpider, self).__init__(*args, **kwargs)
        self.download_dir = download_dir

    def parse(self, response):
        # Extract URLs from the index page
        # version
        release_date = response.css('p.description strong::text').get()
        needs_update = self.update_version(release_date)

        if needs_update == False:
            print("[cedict] already update-to-date")
            return

        # Get download links
        links = response.css('p.description a::attr(href)').getall()
        for link in links:
            if link.endswith('_mdbg.zip'):
                # print(f"Download link: {link}")
                yield Request(
                    url = f"{self.base_url}/{link}",
                    callback = self.download_file,
                )

    def update_version(self, version):
        path = f"{self.download_dir}/VERSION"
        current_version = read_file(path)
        if current_version == version:
            return False
        write_file(path, version)
        return True

    def download_file(self, response):
        # print(response)
        # print(self.download_dir)
        # print(response.url)

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # Generate a filename from the URL
        file_name = os.path.basename(urlparse(response.url).path)
        file_path = os.path.join(self.download_dir, file_name)

        if os.path.exists(file_path):
            print(f"[exists] {file_path}")
            return

        try:
            with open(file_path, 'wb') as f:
                f.write(response.body)
            print(f"[new] {file_path}")
        except Exception as e:
            # self.logger.error(f"Failed to download {response.url}: {str(e)}")
            print(f"Failed to download {response.url}: {str(e)}")
        pass

def run_spider(download_dir):
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
    process.crawl(CedictSpider, download_dir = download_dir)
    process.start()
