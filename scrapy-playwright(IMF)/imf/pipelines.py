from scrapy.pipelines.files import FilesPipeline

class CustomFilePipelines(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return item.get("Title")+'.pdf'
        # print("(Downloaded)___", item.get("Title")+'.pdf')