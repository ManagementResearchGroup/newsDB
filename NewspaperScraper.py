import re

import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article
import logging

logging.basicConfig(level=logging.DEBUG, filename='news.log', format='%(asctime)s %(levelname)s:%(message)s')


def dprint(string):
    debug = 1
    if debug == 1:
        print(string)


class NewspaperScraper:
    def __init__(self, newspaper, searchTerm, dateStart, dateEnd):
        self.newspaper = newspaper
        self.searchTerm = searchTerm
        self.dateStart = parse(dateStart)
        self.dateEnd = parse(dateEnd)
        self.links = []

    def get_newspaper_name(self):
        return self.newspaper

    def get_pages(self):
        print('Unimplemented for ' + self.newspaper + ' scraper')
        return

    def check_dates(self, date):
        page_date = parse(date.replace("ET", ""))
        if page_date >= self.dateStart and page_date <= self.dateEnd:
            return True
        return False

    def newspaper_parser(self, sleep_time=3):
        print('running newspaper_parser()...')

        results = []
        count = 0

        for l in self.links:
            article = Article(url=l)
            try:
                article.download()
                article.parse()
                article.nlp()
            except:
                time.sleep(20)
                continue
            data = {
                'title': article.title,
                'date_published': article.publish_date,
                'news_outlet': self.newspaper,
                'authors': article.authors,
                'feature_img': article.top_image,
                'article_link': article.canonical_link,
                'keywords': article.keywords,
                'movies': article.movies,
                'summary': article.summary,
                'text': article.text,
                'html': article.html}


            results.append(data)

            count += 1
            time.sleep(sleep_time)

        return results

    def write_to_csv(self, data, file_name):
        print('writing to CSV...')

        keys = list(data[0].keys())
        with open(file_name, 'w', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys, delimiter='|')
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def write_to_mongo(self, data, collection):
        print('writing to mongoDB...')
        count = 0

        for d in data:
            collection.insert(d)
            count += 1

    def write_to_json(self, data, filename):
        import json
        with open(filename, 'w') as fp:
            json.dump(data, fp)


class NewspaperScraperWithAuthentication(NewspaperScraper):
    def __init__(self, newspaper, searchTerm, dateStart, dateEnd, userID, password):
        NewspaperScraper.__init__(self, newspaper, searchTerm, dateStart, dateEnd)
        self.userId = userID
        self.password = password

        if newspaper == 'New York Times':
            self.credentials = {
                'userid': userID,
                'password1': password
            }
            self.login_url = 'https://myaccount.nytimes.com/auth/login'
            self.submit_id = 'submit'
        elif newspaper == 'Wall Street Journal':
            self.credentials = {
                'username': userID,
                'password': password
            }
            self.login_url = 'https://id.wsj.com/access/pages/wsj/us/signin.html'
            self.submit_id = 'basic-login-submit'

    def newspaper_parser(self, sleep_time=5):
        logging.debug('running newspaper_parser() for sercure sites...')
        results = []
        count = 0

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(executable_path=r'gecko\geckodriver.exe')
        credential_names = list(self.credentials.keys())

        browser.get(self.login_url)
        cred1 = browser.find_element_by_id(credential_names[0])
        cred2 = browser.find_element_by_id(credential_names[1])
        cred1.send_keys(self.credentials[credential_names[0]])
        cred2.send_keys(self.credentials[credential_names[1]])
        time.sleep(10)
        browser.find_element_by_class_name(self.submit_id).click()
        time.sleep(10)

        cookies = browser.get_cookies()
        browser.close()

        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        for l in self.links:
            try:
                page = s.get(l)
            except Exception as e:
                logging.error("issue bundling {} for {}, {}".format(l, self.searchTerm, e))
                print(e)
                time.sleep(20)
                continue

            soup = BeautifulSoup(page.content, features="lxml")
            article = Article(url=l)
            article.set_html(str(soup))

            article.parse()
            article.nlp()
            up_date = article.publish_date
            if self.newspaper == 'Wall Street Journal':
                soup = BeautifulSoup(article.html, features="lxml")
                # if no articles, stop
                pub_date = soup.find("meta", {"name": "article.published"}).get("content", None)
                up_date = soup.find("meta", {"name": "article.updated"}).get("content", None)
                article.publish_date = pub_date

            data = {
                'search': self.searchTerm,
                'title': article.title,
                'date_published': article.publish_date,
                'date_updated': up_date,
                'news_outlet': self.newspaper,
                'authors': article.authors,
                # 'feature_img': article.top_image,
                'article_link': article.canonical_link,
                'keywords': article.keywords,
                # 'movies': article.movies,
                'summary': article.summary,
                'text': article.text,
                'html': article.html,
            }
            results.append(data)
            time.sleep(sleep_time)

            count += 1
        print("done for ", self.searchTerm)
        return results


class WSJScraper(NewspaperScraperWithAuthentication):

    # get links to articles from search, sleep time is sleep between every page
    def get_pages(self, sleep_time=5):
        logging.debug("running get_pages()...  or search")
        links = []
        stop = False
        index = 1
        # if there are links on the page
        while not stop:
            # move to next page
            page = requests.get('http://www.wsj.com/search/term.html?KEYWORDS='
                                + self.searchTerm
                                + '&min-date=' + str(self.dateStart.date()).replace('-', '/')
                                + '&max-date=' + str(self.dateEnd.date()).replace('-', '/')
                                + '&page=' + str(index)
                                + '&isAdvanced=true&daysback=4y&andor=AND&sort=date-desc&source=wsjarticle,wsjblogs,sitesearch')
            soup = BeautifulSoup(page.content, features="lxml")
            # if no articles, stop
            if soup.find('div', class_="headline-item") is None:
                stop = True
                continue
                logging.debug("no headline found for {} after {} pages".format(self.searchTerm, index))
            # if articles, for every article in search:
            for result in soup.find_all('div', class_="headline-item"):
                #print(result)
                pub_date = result.find('time', class_='date-stamp-container').get_text()
                # check if date is within range, if it is, extract links
                if self.check_dates(pub_date):
                    link = result.find('h3', class_="headline")
                    ltext = link.find('a').get('href')
                    #print(ltext)
                    if 'http://' not in ltext:
                        ltext = 'http://www.wsj.com' + ltext
                    if "http://www.wsj.comhttps://www.wsj.com/" in ltext:
                        #print("relpace", ltext)
                        ltext = ltext.replace('http://www.wsj.comhttps://www.wsj.com/', 'http://www.wsj.com/')
                        #print(ltext)
                    if ltext not in links and 'video' not in ltext:
                            #print(ltext)
                            links.append(ltext)
            index += 1
            time.sleep(sleep_time)

        self.links = links
        logging.debug("{} found for  {}".format(len(links), self.searchTerm))
        print(len(links), "found for ", self.searchTerm)
        #for l in links:
            #print(l)
        return links

#
# pub_date = pub_date.replace("Updated", "")
#                import calendar
#                abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
#                pub_date = pub_date.split()
#                month = abbr_to_num[str(pub_date[0].replace(".", ""))]
#                day = pub_date[1].replace(",", "")
#                year = pub_date[2]
#                daytime = pub_date[4]
#                ttime = pub_date[3].split(":")
#                minute = ttime[1]
#                if daytime == "am":
#                    hour = ttime[0]
#                else:
#                    hour = int(ttime[0]) + 12
#                    if hour == 24:
#                        hour -= 1
#                import datetime
#                dprint([int(year), int(month), int(day), int(hour), int(minute)])
#                pub_date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)).strftime("%m/%d/%Y %H:%M:%S")
#                publish_date = pub_date
