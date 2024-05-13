import json

import pydash
from scrapy.spiders import SitemapSpider


class Scraper(SitemapSpider):
    name = 'meesho'
    allowed_domains = [
        'meesho.com'
    ]
    sitemap_urls = [
        'https://meesho.com/sitemap.xml'
    ]

    def sitemap_filter(self, entries):
        '''
            Filtering sitemap links
        '''
        for entry in entries:
            if not entry.get('priority'):
                yield entry

    def parse(self, response, **kwargs):
        product_list = response.xpath(
            '//div[contains(@class, "ProductList__GridCol")]/a/@href'
        )

        for product in product_list:
            yield response.follow(
                response.urljoin(product.get()),
                self.parse_product_page
            )

        next_page = response.xpath(
            '//div[contains(@class, "Pagination__PaginationItem")]/self::*[boolean(@selected)]/@id'
        ).get()

        # Pagination
        if next_page:
            next_page = int(next_page)+1
            next_page_url = response.url

            if next_page_url.find('?page=') > -1:
                next_page_url = next_page_url.split('?page=')[0]

            next_page_url = '{}?page={}'.format(next_page_url, next_page)

            yield response.follow(
                next_page_url,
                self.parse
            )

    def parse_product_page(self, response, **kwargs):
        '''
            This function is used parse the product page data
        '''
        data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data = json.loads(data)

        data = pydash.get(
            data, 'props.pageProps.initialState.product.details.data'
        )

        product_details = {
            'url': response.url,
            'html': str(response.text)
        }

        list_keys = [
            ('name', 'title'),
            ('description', 'description'),
            ('images', 'images'),
            ('transient_price', 'price'),
            ('original_price', 'original_price'),
            ('supplier_name', 'vendor'),
            ('supplier_average_rating', 'vendor_review'),
            ('variations', 'size')
        ]

        for keys in list_keys:
            key, new_key = keys
            if data.get(key):
                product_details[new_key] = data[key]

        product_details['review'] = pydash.get(
            data, 'review_summary.data.average_rating'
        )

        yield product_details
