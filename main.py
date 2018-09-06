from scrapy.crawler import CrawlerProcess
import youtube_all1
import youtube_all2
import youtube_all3
import youtube_all4


process = CrawlerProcess()
process.crawl(youtube_all1.MusicSpider1)
process.crawl(youtube_all2.MusicSpider2)
process.crawl(youtube_all3.MusicSpider3)
process.crawl(youtube_all4.MusicSpider4)

process.start()
