from scrapy.exporters import CsvItemExporter


class CSVCustomSeperator(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        kwargs['delimiter'] = '|'
        super(CSVCustomSeperator, self).__init__(*args, **kwargs)
