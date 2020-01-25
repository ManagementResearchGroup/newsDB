
class ChicagoTribuneScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 1

        while not stop:
            browser.get('http://www.chicagotribune.com/search/dispatcher.front?page='
                        + str(index)
                        + '&sortby=display_time%20descending&target=stories&spell=on&Query='
                        + self.searchTerm
                        + '#trb_search')

            soup = BeautifulSoup(browser.page_source)

            if not soup.find('div', class_='trb_search_results'):
                stop = True

            for result in soup.find_all('div', class_="trb_search_result_wrapper"):
                pub_date = result.find('time', class_='trb_search_result_datetime').get('data-dt')
                if ':' in pub_date:
                    pub_date = str(datetime.now(timezone('America/Chicago')).date())

                if self.check_dates(pub_date):
                    link = result.find('a', class_='trb_search_result_title')
                    ltext = 'http://www.chicagotribune.com' + link.get('href')

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            index += 1
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links


class LaTimesScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 1

        while not stop:
            browser.get('http://www.latimes.com/search/dispatcher.front?page='
                        + str(index)
                        + '&sortby=display_time%20descending&target=stories&spell=on&Query='
                        + self.searchTerm
                        + '#trb_search')

            soup = BeautifulSoup(browser.page_source)

            if not soup.find('div', class_='trb_search_results'):
                stop = True

            for result in soup.find_all('div', class_="trb_search_result_wrapper"):
                pub_date = result.find('time', class_='trb_search_result_datetime').get('data-dt')
                if ':' in pub_date:
                    pub_date = str(datetime.now(timezone('US/Pacific')).date())

                if self.check_dates(pub_date):
                    link = result.find('a', class_='trb_search_result_title')
                    ltext = 'http://www.latimes.com' + link.get('href')

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            index += 1
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links


class WashPostScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        browser = webdriver.Chrome()

        links = []
        stop = False
        index = 0

        while not stop:
            browser.get('https://www.washingtonpost.com/newssearch/'
                        + '?utm_term=.94befa345ad6&query='
                        + self.searchTerm
                        + '&sort=Date&datefilter=12%20Months&contenttype=Article'
                        + '&spellcheck&startat=' + str(index) + '#top')

            soup = BeautifulSoup(browser.page_source)
            if not soup.find_all('div', class_="pb-feed-item"):
                stop = True
                continue

            for result in soup.find_all('div', class_="pb-feed-item"):
                if self.check_dates(result.find('span', class_='pb-timestamp').get_text()):
                    link = result.find('a', class_="ng-binding")
                    ltext = link.get('href')

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            index += 20
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links


class SlateScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        browser = webdriver.Chrome()

        links = []
        stop = False

        browser.get('http://www.slate.com/search.html#search=' + self.searchTerm)

        while not stop:
            soup = BeautifulSoup(browser.page_source)

            for result in soup.find_all('div', class_="full-width left-image"):
                if self.check_dates(result.find('span', class_='timestamp').get_text()):
                    ltext = result.find('a').get('href')
                    section = self.get_section(ltext)

                    if (section == 'articles' or section == 'blogs') and ltext not in links:
                        print(ltext)
                        links.append(ltext)

            header = soup.find('header', class_="tag-header").get_text().split()
            if int(header[2].split('-')[1]) == int(header[4]):
                stop = True

            try:
                element = browser.find_element_by_xpath('//*[@id="search_content"]/p/a')
                ActionChains(browser).move_to_element(element) \
                    .click(element) \
                    .perform()
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "search_results")))

            except:
                stop = True

            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links

    def get_section(self, href):
        href = href[20:]
        try:
            return re.search('/.*?/', href).group(0)[1:-1]
        except:
            return 'error'


class FoxNewsScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 0

        while not stop:
            browser.get('http://www.foxnews.com/search-results/search?q='
                        + self.searchTerm
                        + '&ss=fn&sort=latest&type=story'
                        + '&min_date=' + str(self.dateStart.date()) + '&max_date=' + str(self.dateEnd.date())
                        + '&start='
                        + str(index))

            soup = BeautifulSoup(browser.page_source)
            if not soup.find_all('div', class_="search-info"):
                stop = True
                continue

            for result in soup.find_all('div', class_="search-info"):
                if self.check_dates(result.find('span', class_='search-date').get_text()):
                    link = result.find('h3').find('a')
                    ltext = link.get('href')
                    section = self.get_section(ltext)

                    if section != 'v' and ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            index += 10
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links

    def get_section(self, href):
        href = href[22:]
        try:
            section = re.search('/.*?/', href).group(0)[1:-1]
            if (section == 'politics' or section == 'us' or section == 'opinion' or section == 'v'):
                return section
            else:
                return 'other'
        except:
            return 'error'


class PoliticoScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        links = []
        stop = False
        index = 1

        while not stop:
            page = requests.get('http://www.politico.com/search/' + str(index) + '?s=newest&q=' + self.searchTerm)
            soup = BeautifulSoup(page.content)

            for result in soup.find_all('article', class_='story-frag format-ml'):
                pub_date = result.find('p', class_='timestamp')
                if pub_date is None:
                    continue

                if self.check_dates(pub_date.get_text().split()[0]):
                    try:
                        link = result.find('h3').find('a')
                        ltext = link.get('href')
                        section = self.get_section(ltext)
                    except:
                        continue

                    if (section == 'story' or section == 'blogs') and ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            index += 1
            time.sleep(sleep_time)

        # browser.close()
        self.links = links
        return links

    def get_section(self, href):
        href = href[23:]
        try:
            return re.search('/.*?/', href).group(0)[1:-1]
        except:
            return 'error'


class WeeklyStandardScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        browser = webdriver.Chrome()

        links = []
        stop = False

        browser.get('http://www.weeklystandard.com/search?query=' + self.searchTerm)

        while not stop:
            soup = BeautifulSoup(browser.page_source)

            for result in soup.find_all('div', class_="data-item"):
                if self.check_dates(result.find('div', class_='item-pubdate').get_text()):
                    link = result.find('div', class_="item-headline").find('a')
                    ltext = link.get('href')

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            try:
                element = browser.find_element_by_xpath('//*[@id="resultdata"]/div[22]/a')
                ActionChains(browser).move_to_element(element) \
                    .click(element) \
                    .perform()
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "resultdata")))

            except:
                stop = True

            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links


class BloombergScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 1
        days = (self.dateEnd.date() - self.dateStart.date()).days + 1

        while not stop:
            browser.get('https://www.bloomberg.com/search?query='
                        + self.searchTerm
                        + '&startTime=-' + str(days) + 'd'
                        + '&sort=time:desc'
                        + '&endTime=' + str(self.dateEnd.date()) + 'T23:59:59.999Z'
                        + '&page=' + str(index))

            soup = BeautifulSoup(browser.page_source)

            if soup.find('div', class_="search-result-story__container") is None:
                stop = True
                continue

            for result in soup.find_all('div', class_="search-result-story__container"):
                if self.check_dates(result.find('span', class_='metadata-timestamp').get_text()):
                    link = result.find('h1', class_="search-result-story__headline")
                    ltext = link.find('a').get('href')
                    section = self.get_section(ltext)

                    if section == 'articles' and ltext not in links:
                        print(ltext)
                        links.append(ltext)

            index += 1
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links

    def get_section(self, href):
        href = href[25:]
        try:
            return re.search('/.*?/', href).group(0)[1:-1]
        except:
            return 'error'


class TimeScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 1

        while not stop:
            browser.get('http://search.time.com/?q=' + self.searchTerm + '&startIndex=' + str(index) + '&sort=Date')
            soup = BeautifulSoup(browser.page_source)

            for result in soup.find_all('div', class_="content-right"):
                pub_date = result.find('div', class_='content-snippet').get_text().split('...')[0].strip()
                if 'hour' in pub_date:
                    pub_date = str((datetime.now(timezone('EST')) - timedelta(hours=int(pub_date[0]))).date())
                elif 'day' in pub_date:
                    pub_date = str((datetime.today() - timedelta(days=int(pub_date[0]))).date())

                if self.check_dates(pub_date):
                    link = result.find('div', class_="content-title")
                    ltext = link.find('a').get('href')

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

                else:
                    stop = True
                    break

            error_message = soup.find('div', class_="search-results-message")
            if error_message:
                if error_message.get_text() == 'Error getting Search Results':
                    stop = True

            index += 10
            time.sleep(sleep_time)

        browser.close()
        self.links = links
        return links


class CNNScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        browser = webdriver.Chrome()

        links = []
        index = 0

        browser.get('http://www.cnn.com/search/?text=' + self.searchTerm)
        soup = BeautifulSoup(browser.page_source)
        search_results = int(soup.find('div', class_='cn cn--idx-0 search-results_msg').get_text().split()[4])

        while index < search_results:
            soup = BeautifulSoup(browser.page_source)

            for result in soup.find_all('article',
                                        class_="cd cd--card cd--idx-0 cd--large cd--horizontal cd--has-media"):
                pub_date = result.find('span', class_='cd__timestamp').get_text()
                if not pub_date:
                    continue
                if ':' in pub_date:
                    pub_date = pub_date.split(',')
                    pub_date = (pub_date[1] + ',' + pub_date[2]).strip()

                if self.check_dates(pub_date):
                    link = result.find('h3', class_="cd__headline").find('a')
                    ltext = link.get('href')

                    if 'http://' not in ltext:
                        ltext = 'http://www.cnn.com' + ltext

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

            index += 10
            time.sleep(sleep_time)

            try:
                element = browser.find_element_by_xpath('//*[@id="cnnSearchPagination"]/div/div[3]/a/span[1]')
                ActionChains(browser).move_to_element(element) \
                    .click(element) \
                    .perform()
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "textResultsContainer")))

            except:
                continue

        browser.close()
        self.links = links
        return links


class CNBCScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        links = []
        stop = False
        index = 1
        days = (self.dateEnd.date() - self.dateStart.date()).days + 1

        while not stop:
            page = requests.get('http://search.cnbc.com/rs/search/view.html?partnerId=2000'
                                + '&keywords=' + self.searchTerm
                                + '&sort=date&type=news&source=CNBC.com'
                                + '&pubtime=' + str(days) + '&pubfreq=d'
                                + '&page=' + str(index))
            soup = BeautifulSoup(page.content)

            if soup.find('div', class_="SearchResultCard") is None:
                stop = True
                continue

            for result in soup.find_all('div', class_="SearchResultCard"):
                seconds_since_epoch = float(re.findall(r'\d+', result.find('time').get_text())[0])
                pub_date = str(datetime.fromtimestamp(seconds_since_epoch / 1000).replace(hour=0, minute=0, second=0,
                                                                                          microsecond=0))

                if self.check_dates(pub_date):
                    link = result.find('h3', class_="title")
                    ltext = link.find('a').get('href')
                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)

            index += 1
            time.sleep(sleep_time)

        self.links = links
        return links


class USATodayScraper(NewspaperScraper):
    def get_pages(self, sleep_time=5):
        print('running get_pages()...')

        browser = webdriver.Chrome()
        browser.get('http://www.usatoday.com/search/' + self.searchTerm + '/')

        links = []
        stop = False
        index = 1

        element = browser.find_element_by_xpath('/html/body/div[2]/div[1]/div/div[3]/span[2]')
        ActionChains(browser).move_to_element(element) \
            .click(element) \
            .perform()

        lastHeight = browser.execute_script("return document.body.scrollHeight")
        tries = 0

        while not stop:
            soup = BeautifulSoup(browser.page_source)
            # print soup.find_all('li', class_=' search-result-item')
            last_search_item = soup.find_all('li', class_=' search-result-item')[-1]
            link = last_search_item.find('a', class_='search-result-item-link').get('href')
            date_match = re.search('([0-9]{4}/[0-9]{2}/[0-9]{2})', link)
            if date_match is not None:
                print(date_match.group(1))

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_time)

            newHeight = browser.execute_script("return document.body.scrollHeight")
            if (newHeight == lastHeight):
                tries += 1
                time.sleep(5)
                if tries >= 5:
                    stop = True
            else:
                tries = 0

            lastHeight = newHeight

        soup = BeautifulSoup(browser.page_source)

        for result in soup.find_all('li', class_=' search-result-item'):
            link = result.find('a', class_='search-result-item-link').get('href')
            date_match = re.search('([0-9]{4}/[0-9]{2}/[0-9]{2})', link)

            if date_match is not None:
                if self.check_dates(date_match.group(1)):
                    ltext = 'http://www.usatoday.com/' + link

                    if ltext not in links:
                        print(ltext)
                        links.append(ltext)
                else:
                    continue

            index += 1

        browser.close()
        self.links = links
        return links



class NYTScraper(NewspaperScraperWithAuthentication):
    def get_pages(self, sleep_time=5):
        print('running get_pages()...')

        profile = webdriver.FirefoxProfile()
        browser = webdriver.Firefox(profile)

        links = []
        stop = False
        index = 1
        current_start = (self.dateEnd - timedelta(days=6)).date()
        current_end = self.dateEnd.date()

        while not stop:
            while True:
                browser.get('http://query.nytimes.com/search/sitesearch/?action=click&contentCollection'
                            + '&region=TopBar&WT.nav=searchWidget&module=SearchSubmit&pgtype=Homepage#/'
                            + self.searchTerm
                            + '/from' + str(current_start).replace('-', '') + 'to' + str(current_end).replace('-', '')
                            + '/allresults/'
                            + str(index)
                            + '/allauthors/newest/')

                time.sleep(sleep_time)
                soup = BeautifulSoup(browser.page_source)

                for result in soup.find_all('li', class_="story"):
                    pub_div = result.find('span', class_='dateline')
                    if pub_div is None:
                        continue

                    if self.check_dates(pub_div.get_text()):
                        link = result.find('div', class_='element2')
                        ltext = link.find('a').get('href')
                        section = self.get_section(ltext)

                        if section != 'video' and ltext not in links:
                            # print ltext
                            print(pub_div.get_text())
                            links.append(ltext)

                    else:
                        stop = True
                        break

                next_page = soup.find('a', class_="stepToPage next")
                if not next_page and index == 1:
                    continue
                elif not next_page or stop is True:
                    break

                index += 1

            current_start = current_start - timedelta(days=7)
            current_end = current_end - timedelta(days=7)
            index = 1

        browser.close()
        self.links = links
        return links

    def get_section(self, href):
        href = href[22:]
        try:
            return re.search('/.*?/', href).group(0)[1:-1]
        except:
            return 'error'''
