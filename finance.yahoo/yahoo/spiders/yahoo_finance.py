import scrapy
from scrapy_playwright.page import PageMethod


def should_abort_request(request):
    if request.resource_type == "image" or request.resource_type == "ping":
        return True
    return False


class YahooFinanceSpider(scrapy.Spider):
    name = "yahoo-finance"

    custom_settings = {"PLAYWRIGHT_ABORT_REQUEST": should_abort_request}

    url = "https://finance.yahoo.com"  # home (Approx. 60%+ Ad)
    url2 = "https://finance.yahoo.com/news"  # news (25% Ad)

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) Safari/537.36
    def start_requests(self):
        yield scrapy.Request(
            # self.url,
            self.url2,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods={
                    # ---for url ('https://finance.yahoo.com')---
                    # PageMethod('wait_for_selector', 'div#slingstoneStream-0-Stream ul li:nth-child(10)'),
                    # ---for url2 ('https://finance.yahoo.com/news')---
                    PageMethod(
                        "wait_for_selector", "div#Fin-Stream ul li:nth-child(10)"
                    ),
                },
            ),
            errback=self.close_page,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        # There are maximum 200 data include Ad (19 times loop)
        # Infinite scrolling up to 19 times
        for i in range(2, 21):
            # Handling timed out error to prevent crash
            try:
                await page.keyboard.press("End")

                # ---for url ('https://finance.yahoo.com')---
                # await page.wait_for_selector(f'div#slingstoneStream-0-Stream ul li:nth-child({i*10})')

                # ---for url2 ('https://finance.yahoo.com/news')---
                await page.wait_for_selector(f"div#Fin-Stream ul li:nth-child({i*10})")
            except:
                break

        html = await page.content()
        selected = scrapy.Selector(text=html)
        await page.close()
        # ---for url ('https://finance.yahoo.com')---
        # articles = selected.css('div#slingstoneStream-0-Stream ul li.js-stream-content')

        # ---for url2 ('https://finance.yahoo.com/news')---
        articles = selected.css("div#Fin-Stream ul li.js-stream-content")

        # Parsing all url of all articles and request for full content
        for item in articles:
            url: str = item.css("a.js-content-viewer ::attr(href)").get()
            # url is not end with '.html' and start with 'm/' are Ad
            # Excluding Ad url
            if (
                url is not None
                and url.endswith(".html")
                and url is not url.startswith("m/")
            ):
                if url.startswith("https") or url.startswith("http"):
                    yield scrapy.Request(url, callback=self.parse_content)
                else:
                    yield scrapy.Request(
                        response.urljoin(url), callback=self.parse_content
                    )

    # Parsing full article
    def parse_content(self, response):
        article = response.css("article")
        title = article.css("header h1 ::text").get()
        body = article.css("div.caas-body p ::text").extract()
        body_string = " ".join(body)

        yield {"title": title, "body": body_string}

    # Closing page if browser throw error
    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
