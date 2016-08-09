Before opening the ISUScraper python script you will need these Python Modules/packages:
csv
BeautifulSoup
urlopen
requests
urljoin
urlparse
re
os

And you will need the file that gives the base domain for the ISU websites that will be scraped. The python package calls for the document to be called: 'homepages.csv' That file is within the dropbox and GitHUB

For this year the base URL is http://www.isuresults.eu/index.html

The output of the data is mainly in the 'Racer.csv' and 'Titles.csv' files. In racer will be the laptimes of the racers, and in titles will be the weather and event title. Another file of 'trulyfailedURLs.csv' will contain websites that the scraper was not able to get data from (typically PDFs)
