#!/usr/bin/env uv run
#
# autor: Ethan Liu
#
# cc-cedict spider
#
# https://www.mdbg.net/chinese/dictionary?page=cc-cedict
# https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip


# import os
from pathlib import Path
from urllib.parse import urlparse
# from lib.util import read_file, write_file

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class CedictSpider(Spider):
    name = 'cedict'
    start_urls = ['https://www.mdbg.net/chinese/dictionary?page=cc-cedict']
    # start_urls = ['http://localhost/tmp/cedict.html']
    base_url = 'https://www.mdbg.net/chinese'
    download_dir: Path

    def __init__(self, download_dir=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download_dir = Path(download_dir) if download_dir else Path('downloads')

    def parse(self, response):
        release_date = response.css('p.description strong::text').get()

        # update_version returns a boolean
        if not self.update_version(release_date):
            print("❌ Already up-to-date")
            return

        links = response.css('p.description a::attr(href)').getall()
        for link in links:
            if link.endswith('_mdbg.zip'):
                yield Request(
                    url=f"{self.base_url}/{link}",
                    callback=self.download_file
                )

    def update_version(self, version: str) -> bool:
        # Ensure we are working with a Path object
        dir_path = Path(self.download_dir)
        version_file = dir_path / "VERSION"

        dir_path.mkdir(parents=True, exist_ok=True)

        # Use path.read_text() instead of custom read_file if you want to drop lib.util
        if version_file.exists() and version_file.read_text(encoding='utf-8') == version:
            return False

        version_file.write_text(version, encoding='utf-8')
        return True


    def download_file(self, response: Response):
        url_path = urlparse(response.url).path
        file_name = Path(url_path).name
        file_path = self.download_dir / file_name

        if file_path.exists():
            self.logger.warning(f"❌ same version already exists: {file_path.name}")
            return

        try:
            file_path.write_bytes(response.body)
            self.logger.info(f"✅ new version downloaded: {file_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to download {response.url}: {e}")

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
