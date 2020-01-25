from RunScrapers import initialize_scraper
import csv

number_of_companies = 50
companies = []

with open('fortune500.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    row_count = 0
    for row in csv_reader:
        if row_count < number_of_companies:
            companies.append(row[1])
            row_count += 1

print(companies)
date_max = "12-31-2019"
date_min = "01-01-2019"
for c in companies:
    initialize_scraper([0, "Wall Street Journal", c, date_min, date_max, "marcel@tkacik.cz", "researchPrague3"])
