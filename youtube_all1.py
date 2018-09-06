#!/usr/bin/python3
import scrapy
import json
import pprint
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from urlparse import urlparse
from scrapy.utils.response import open_in_browser
import sys
import time
from selenium import webdriver
import csv
import xml.dom.minidom
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import MySQLdb
from MySQLdb import escape_string



class MusicSpider1(scrapy.Spider):

    name = "youtube_charts_songs_trends1"
    global lastthursdate
    start_urls = ["https://charts.youtube.com/"]

    db = MySQLdb.connect("ip", "database_name", "pwd", "table", use_unicode=True, charset="utf8")
    x = db.cursor()

    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        with open('urls.csv') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if(row['type'] == 'Trending Videos'):
                    yield Request(row['url'], meta={'country': row['country'], 'type': row['type']}, callback=self.each_detail)

    def each_detail(self, response):
        now = datetime.datetime.now()
        driver2 = webdriver.Chrome()
        driver2.get(response.url)
        country = response.meta['country']
        url_type = response.meta['type']

        if url_type == 'Trending Videos':
            try:
                element = WebDriverWait(driver2, 10000).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")))
            except Exception, e:
                print "waited 5 sec"

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")


            # this also includes the 10 artist of top artist list due to xpath strcuture
            song = []

            print(len(new_element))
            for elements in new_element:
                song += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[2]/ytmc-ellipsis-text/div/span")

            artist = []

            print(len(new_element))
            for elements in new_element:
                artist += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text")



            url = []

            print(len(new_element))
            i = 0
            for elements in new_element:
                i += 1
                try:
                    dict_rep = json.loads(elements.get_attribute("endpoint"))
                    url += [dict_rep['urlEndpoint']['url']]
                except Exception, e:
                    url += [""]

            print "-------------------"
            print country
            print artist
            print song
            print url

            i = 0
            sql = ""
            for temp_song in song:
                rank = i + 1
                sql = "INSERT INTO songs_chart_temp (Artist,Song,Chart_name,Chart_name_2,Chart_type,Rank,Date,YTURL) values(%s, %s, %s,%s, %s,%s,%s,%s)"

                try:
                    if self.x.execute(sql, (artist[i], temp_song, url_type, country, "YouTube", escape_string(str(rank)), now, url[i])):
                        print "item Inserted"
                    else:
                        print "Something wrong"

                except Exception, e:
                    raise e

                i = i + 1
        elif url_type == 'Top Artists':
            try:
                element = WebDriverWait(driver2, 10000).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart-table-row')]/div[2]/div/ytmc-ellipsis-text/div/span")))
            except Exception, e:
                print "waited 5 sec"

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[2]/div/ytmc-ellipsis-text/div/span")

            artist = []

            print(len(new_element))
            for elements in new_element:
                artist += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[2]/div/ytmc-ellipsis-text")
            url = []

            print(len(new_element))
            i = 0
            for elements in new_element:
                i += 1
                try:
                    dict_rep = json.loads(elements.get_attribute("endpoint"))
                    url += [dict_rep['urlEndpoint']['url']]
                except Exception, e:
                    url += [""]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[1]/div[2]/span")

            last_week = []

            print(len(new_element))
            for elements in new_element:
                text = elements.text.replace("last week #", "")
                text = text.replace("--", "")
                last_week += [text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[5]/div/span")

            views = []

            print(len(new_element))
            for elements in new_element:
                views += [int(value_to_float(elements.text.replace("<","")))]


            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[4]/div/span")
            change = []

            print(len(new_element))
            for elements in new_element:
                value = elements.text.replace("%", "").replace("--", "")
                if value == "":
                    value = float(0)
                else:
                    value = float(value)/100
                change += [value]

            print "-------------------"
            print country
            print artist
            print(len(artist))
            print url
            print(len(url))
            print last_week
            print(len(last_week))
            print views
            print(len(views))
            print change
            print(len(change))

            i = 0
            sql = ""
            for temp_artist in artist:
                rank = i + 1
                sql = "INSERT INTO songs_chart_temp (Artist, Song, Chart_name,Chart_name_2,Chart_type,Rank,Date,YTURL, rank_prev, YTDailyViews, audience_move) values(%s, %s, %s,%s, %s,%s,%s, %s, %s, %s, %s)"
                try:
                    if self.x.execute(sql, (temp_artist, "[Artist]", url_type, country, "YouTube", escape_string(str(rank)), now, url[i], last_week[i], views[i], change[i])):
                        print "item Inserted"
                    else:
                        print "Something wrong"

                except Exception, e:
                    raise e

                i = i + 1
        elif url_type == 'Top Music Videos':
            try:
                element = WebDriverWait(driver2, 10000).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")))
            except Exception, e:
                print "waited 5 sec"

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")


            # this also includes the 10 artist of top artist list due to xpath strcuture
            song = []

            print(len(new_element))
            for elements in new_element:
                song += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[2]/ytmc-ellipsis-text/div/span")

            artist = []

            print(len(new_element))
            for elements in new_element:
                artist += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text")



            url = []

            print(len(new_element))
            i = 0
            for elements in new_element:
                i += 1
                try:
                    dict_rep = json.loads(elements.get_attribute("endpoint"))
                    url += [dict_rep['urlEndpoint']['url']]
                except Exception, e:
                    url += [""]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[1]/div[2]/span")
            last_week = []

            print(len(new_element))
            for elements in new_element:
                text = elements.text.replace("last week #", "")
                text = text.replace("--", "")
                last_week += [text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[6]/div/span")

            views = []

            print(len(new_element))
            for elements in new_element:
                views += [int(value_to_float(elements.text.replace("<","")))]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[5]/div/span")
            change = []

            print(len(new_element))
            for elements in new_element:
                value = elements.text.replace("%", "").replace("--", "")
                if value == "":
                    value = float(0)
                else:
                    value = float(value)/100
                change += [value]

            print "-------------------"
            print country
            print song
            print(len(song))
            print artist
            print(len(artist))
            print url
            print(len(url))
            print last_week
            print(len(last_week))
            print views
            print(len(views))
            print change
            print(len(change))

            i = 0
            sql = ""
            for temp_song in song:
                rank = i + 1
                sql = "INSERT INTO songs_chart_temp (Artist, Song, Chart_name,Chart_name_2,Chart_type,Rank,Date,YTURL, rank_prev, YTDailyViews, audience_move) values(%s, %s, %s,%s, %s,%s,%s, %s, %s, %s, %s)"

                try:
                    if self.x.execute(sql, (artist[i], temp_song, url_type, country, "YouTube", escape_string(str(rank)), now, url[i], last_week[i], views[i], change[i])):
                        print "item Inserted"
                    else:
                        print "Something wrong"

                except Exception, e:
                    raise e

                i = i + 1

        elif url_type == 'Top Songs':
            try:
                element = WebDriverWait(driver2, 10000).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")))
            except Exception, e:
                print "waited 5 sec"

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text/div/span")


            # this also includes the 10 artist of top artist list due to xpath strcuture
            song = []

            print(len(new_element))
            for elements in new_element:
                song += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[2]/ytmc-ellipsis-text/div/span")

            artist = []

            print(len(new_element))
            for elements in new_element:
                artist += [elements.text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[1]/ytmc-ellipsis-text")



            url = []

            print(len(new_element))
            i = 0
            for elements in new_element:
                i += 1
                try:
                    dict_rep = json.loads(elements.get_attribute("endpoint"))
                    url += [dict_rep['urlEndpoint']['url']]
                except Exception, e:
                    url += [""]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[1]/div[2]/span")
            last_week = []

            print(len(new_element))
            for elements in new_element:
                text = elements.text.replace("last week #", "")
                text = text.replace("--", "")
                last_week += [text]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[6]/div/span")

            views = []

            print(len(new_element))
            for elements in new_element:
                views += [int(value_to_float(elements.text.replace("<","")))]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[5]/div/span")
            change = []

            print(len(new_element))
            for elements in new_element:
                value = elements.text.replace("%", "").replace("--", "")
                if value == "":
                    value = float(0)
                else:
                    value = float(value)/100
                change += [value]

            new_element = driver2.find_elements_by_xpath("//div[contains(@class, 'chart-table-row')]/div[3]/div[3]/span")
            label = []

            print(len(new_element))
            for elements in new_element:
                label += [elements.text]

            print "-------------------"
            print country
            print song
            print(len(song))
            print artist
            print(len(artist))
            print url
            print(len(url))
            print last_week
            print(len(last_week))
            print views
            print(len(views))
            print change
            print(len(change))
            print label
            print(len(label))

            i = 0
            sql = ""
            for temp_song in song:
                rank = i + 1
                sql = "INSERT INTO songs_chart_temp (Artist, Song, Chart_name,Chart_name_2,Chart_type,Rank,Date,YTURL, rank_prev, YTDailyViews, audience_move, Label) values(%s, %s, %s,%s, %s,%s,%s, %s, %s, %s, %s, %s)"

                try:
                    if self.x.execute(sql, (artist[i], temp_song, url_type, country, "YouTube", escape_string(str(rank)), now, url[i], last_week[i], views[i], change[i], label[i])):
                        print "item Inserted"
                    else:
                        print "Something wrong"

                except Exception, e:
                    raise e

                i = i + 1

        self.db.commit()


def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0
