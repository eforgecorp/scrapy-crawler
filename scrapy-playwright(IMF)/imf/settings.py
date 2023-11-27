BOT_NAME = "imf"

SPIDER_MODULES = ["imf.spiders"]
NEWSPIDER_MODULE = "imf.spiders"


DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 920000
PLAYWRIGHT_BROWSER_SETTINGS = {
    'headless': True,
}


# ITEM_PIPELINES = {"scrapy.pipelines.files.FilesPipeline": 1}
ITEM_PIPELINES = {"imf.pipelines.CustomFilePipelines": 1}
FILES_STORE = "download"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
