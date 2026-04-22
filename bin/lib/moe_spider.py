#!/usr/bin/env uv run
#
# autor: Ethan Liu
#
# description...
#

#!/usr/bin/env uv run
#
# autor: Ethan Liu
#
# description...
#

# import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class MoeSpider(Spider):
    name = 'moe'
    start_urls = ["https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/index.html"]

    # Declare types for Pylance
    download_dir: Path

    def __init__(self, download_dir: str | Path | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Ensure download_dir is a Path object immediately
        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = Path('downloads/moe')

    def parse(self, response: Response):
        for link in response.css('a'):
            link_text = link.css('::text').get()
            link_url = link.css('::attr(href)').get()

            if link_text and link_url and self.is_content_url(link_text, link_url):
                yield Request(
                    url=response.urljoin(link_url),
                    callback=self.parse_content_page
                )

    def parse_content_page(self, response: Response):
        # Using xpath to find the link following the specific text
        links = response.xpath('//text()[contains(., "文字資料庫")]/following::a[1]/@href').getall()
        for link in links:
            full_url = response.urljoin(link)
            yield Request(
                url=full_url,
                callback=self.download_file,
                meta={'source_url': response.url}
            )

    def is_content_url(self, link_text: str, link_url: str) -> bool:
        if 'dict_mini' in link_url:
            return False
        return '資料下載' in link_text.lower()

    def download_file(self, response: Response):
        # Create directory if it doesn't exist (Swift-like simplicity)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        file_url = response.url
        # Swift: lastPathComponent -> Python: .name
        file_name = Path(urlparse(file_url).path).name
        file_path = self.download_dir / file_name

        if file_path.exists():
            print(f"❌ File exists: {file_name}")
            return

        try:
            # Write binary data directly using Path object
            file_path.write_bytes(response.body)
            print(f"✅ New download: {file_name}")
        except Exception as e:
            self.logger.error(f"Failed to download {file_url}: {e}")

def run_spider(download_dir: str):
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
        'ROBOTSTXT_OBEY': True,
        'MEMUSAGE_ENABLED': False,
        'LOG_LEVEL': 'ERROR',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
    })

    process = CrawlerProcess(settings)
    process.crawl(MoeSpider, download_dir=download_dir)
    process.start()