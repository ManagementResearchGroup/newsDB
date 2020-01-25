import sys
from pymongo import MongoClient
from NewspaperScraper import *

client = MongoClient('localhost', 27017)
db = client.News_database


def run_scraper(scraper):
    # get a list of all links to news articles
    scraper.get_pages()
    # scrape data link by link (open them)
    #data = scraper.newspaper_parser()
    #scraper.write_to_mongo(data, db.articles2019)
    # scraper.write_to_csv(data, "test")
    # scraper.write_to_json(data, "test_json.json")


def initialize_scraper(args):
    print(args)
    if args[1] == 'Chicago Tribune':
        run_scraper(ChicagoTribuneScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Los Angeles Times':
        run_scraper(LaTimesScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Washington Post':
        run_scraper(WashPostScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Slate':
        run_scraper(SlateScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Politico':
        run_scraper(PoliticoScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Fox News':
        run_scraper(FoxNewsScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'The Weekly Standard':
        run_scraper(WeeklyStandardScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Bloomberg':
        run_scraper(BloombergScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'TIME':
        run_scraper(TimeScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'Wall Street Journal':
        run_scraper(WSJScraper(args[1], args[2], args[3], args[4], args[5], args[6]))
    elif args[1] == 'New York Times':
        run_scraper(NYTScraper(args[1], args[2], args[3], args[4], args[5], args[6]))
    elif args[1] == 'CNN':
        run_scraper(CNNScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'USA Today':
        run_scraper(USATodayScraper(args[1], args[2], args[3], args[4]))
    elif args[1] == 'CNBC':
        run_scraper(CNBCScraper(args[1], args[2], args[3], args[4]))


if __name__ == "__main__":
    initialize_scraper(sys.argv)
