import scrapy
from scrapy_playwright.page import PageMethod
import codecs
import math
from pathlib import Path

def should_abort_request(request):
    if request.resource_type == "image" or request.resource_type == "ping" or request.resource_type == "font":
        return True
    return False

class PdfDownloaderSpider(scrapy.Spider):
    name = "pdf_downloader"
    num = None
    page_count = 0
    total_pages = 0
    topics= ['Financial and monetary sector', 'Real sector', 'Fiscal sector', 'External sector', 'Fund operations', 'Cross-sector', 'Economic theory and methods', 'Fund structure and governance', 'Natural resources', 'Environmental policy', 'Environmental sustainability', 'All']

    custom_settings={
        "PLAYWRIGHT_ABORT_REQUEST" : should_abort_request, # skip request
        "PLAYWRIGHT_MAX_CONTEXTS": 20,
        "CONCURRENT_REQUESTS": 32,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 4,
        "CLOSESPIDER_ITEMCOUNT": 1000,
    }

    @classmethod
    def set_num(cls, selected_num):
        cls.num = selected_num

    @classmethod
    def set_page_count(cls, page_number):
        cls.page_count = page_number

    @classmethod
    def set_total_pages(cls, pages):
        cls.total_pages = pages

    # Initial request
    def start_requests(self):
        print('\n\n')
        for index, topic in enumerate(self.topics, start=1):
            print(f"{index}. {topic}")

        # getting topic input for filtering
        selected_num = input('Select a topic by number: ')
        self.set_num(selected_num)

        if(self.topics[int(self.num)-1] == 'All'):
            print(f'\n\nSelected Item: {self.topics[int(self.num)-1]}')
            print('Downloading...')
            print('Please wait a few minutes...\n')
            yield scrapy.Request(
                url='https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50',
                meta=dict(
                    playwright=True,
                    playwright_context = "context-1",
                    playwright_include_page= True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle')
                    ]
                ),
                dont_filter=True,
            )
        elif(int(self.num) <= len(self.topics) and int(self.num) > 0 and self.topics[int(self.num)-1] != 'All'):
            print(f'\n\nSelected Item: {self.topics[int(self.num)-1]}')
            print('Downloading...')
            print('Please wait a few minutes...\n')
            yield scrapy.Request(
                url=f'https://www.imf.org/en/Publications/Search#sort=relevancy&numberOfResults=50&f:topic=[{self.topics[int(self.num)-1]}]',
                meta=dict(
                    playwright=True,
                    playwright_context= "context-1",
                    playwright_include_page= True,
                    playwright_page_methods=[
                        PageMethod('wait_for_load_state', 'networkidle')
                    ]
                ),
                dont_filter=True,
            )
        else:
            print('Wrong input...')
            return

    
    # Parsing first request data and sending request to rest pages
    async def parse(self, response):
        result_count = response.css('div.coveo-summary-section span.CoveoQuerySummary span span.coveo-highlight')
        total_items = result_count[-1]
        items = total_items.css('span.coveo-highlight ::text').get()

        page = response.meta["playwright_page"]
        await page.close()
        await page.context.close()

        result = response.css('div.CoveoResult')
        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }

        self.set_page_count(self.page_count+1)
        print(f'Page {self.page_count}___(Scraped)')
        
        # Paginating all pages except first page
        items_count = int(items.replace(',', '')) # All data count as an int
        
        if(self.topics[int(self.num)-1] == 'All'):
            if items_count >= 1000:
                self.set_total_pages(20)
                
                # Loop over for rest 19 pages, because first 20 page of imf website is available.
                for i in range(1, 20):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50',
                        callback= self.parse_rest,
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                            ]
                        ),
                        dont_filter=True,
                    )
            elif(items_count < 1000 and items_count > 0):
                self.set_total_pages(math.ceil(items_count/50))
                
                # Loop over all pages if data are less then 1000.
                for i in range(1, math.ceil(items_count/50)):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50',
                        callback= self.parse_rest,
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                            ]
                        ),
                        dont_filter=True,
                    )
        elif(int(self.num) < len(self.topics) and int(self.num) > 0 and self.topics[int(self.num)-1] != 'All'):
            if items_count >= 1000:
                self.set_total_pages(20)
                for i in range(1, 20):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50&f:topic=[{self.topics[int(self.num)-1]}]',
                        callback= self.parse_rest,
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                            ]
                        ),
                        dont_filter=True,
                    )
            elif(items_count < 1000 and items_count > 0):
                self.set_total_pages(math.ceil(items_count/50))
                for i in range(1, math.ceil(items_count/50)):
                    yield scrapy.Request(
                        url=f'https://www.imf.org/en/Publications/Search#first={i*50}&sort=relevancy&numberOfResults=50&f:topic=[{self.topics[int(self.num)-1]}]',
                        callback= self.parse_rest,
                        meta=dict(
                            playwright_context = f"context-{(i+1)}",
                            playwright_include_page= True,
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod('wait_for_load_state', 'networkidle'),
                            ]
                        ),
                        dont_filter=True,
                    )
        else:
            return

        print('Paginating...')

    # Parsing rest of the data
    async def parse_rest(self, response):
        page = response.meta["playwright_page"]
        result = response.css('div.CoveoResult')
        await page.close()
        await page.context.close()
        for item in result:
            title = item.css('div.CoveoTemplateLoader h3 a.CoveoResultLink ::text').get()
            link = item.css('div.CoveoResultFolding h4 a.CoveoResultLink ::attr(href)').get()
            if(link):
                yield{
                    "Title": codecs.decode(title[0:50], 'unicode_escape'),
                    "file_urls": [link]
                }
        self.set_page_count(self.page_count+1)
        print(f'Page {self.page_count}___(Scraped)')

        if(self.page_count == self.total_pages):
            print("Downloading pdf...")

