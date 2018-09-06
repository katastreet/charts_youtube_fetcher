#!/usr/bin/python3
import scrapy
from selenium import webdriver
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MusicSpider(scrapy.Spider):

    name = "youtube_charts_songs_trends"
    global lastthursdate
    start_urls = ["https://charts.youtube.com/"]

    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(response.url)

        try:
            element = WebDriverWait(self.driver, 10000).until(EC.presence_of_element_located((By.XPATH, "//paper-listbox[contains(@class, 'dropdown-content')]/paper-item[position()>=1 and position()<=1000]")))
        except Exception, e:
            print "waited 5 sec"

        new_element = self.driver.find_elements_by_xpath("//paper-listbox[contains(@class, 'dropdown-content')]/paper-item[position()>=1 and position()<=1000]")

        trending_videos = "https://charts.youtube.com/charts/TrendingVideos/"
        top_songs = "https://charts.youtube.com/charts/TopSongs/"
        top_music_videos = "https://charts.youtube.com/charts/TopVideos/"
        top_artists = "https://charts.youtube.com/charts/TopArtists/"

        with open('urls.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['url', 'country', 'code', 'type'])
            writer.writeheader()
            for elements in new_element:
                code = elements.get_attribute("option-id")
                country = elements.get_attribute("aria-label")
                if country != "Global":
                    writer.writerow({'url': trending_videos + code, 'country': country, 'code': code, 'type': 'Trending Videos'})
                    writer.writerow({'url': top_songs + code, 'country': country, 'code': code, 'type': 'Top Songs'})
                    writer.writerow({'url': top_music_videos + code, 'country': country, 'code': code, 'type': 'Top Music Videos'})
                    writer.writerow({'url': top_artists + code, 'country': country, 'code': code, 'type': 'Top Artists'})
