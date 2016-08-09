import csv
from bs4 import BeautifulSoup
from urllib2 import urlopen
import requests
from urlparse import urljoin
from urlparse import urlparse
import re
import os

####write header for weather
weatherHeaders = ['SiteID','Start Time','End Time','Air Temp','Ice Temp','Humidity','Title','TimeStamp']
with open('Titles.csv', 'wb') as w:
    writer = csv.writer(w)
    writer.writerow(weatherHeaders)
####Write headers for Racers
RacerHeaders = ['SiteID','Rank','No.','Name','Nation','Sprint Points','Points','Time']
with open('reordered.csv', 'ab') as w:
    writer = csv.writer(w)
    writer.writerow(RacerHeaders)

####Get a list of sites 2016
parenturl = []
#parenturl =['http://www.isuresults.eu/','http://www.isuresults.eu/2014-2015.html','http://www.isuresults.eu/2013-2014.html','http://www.isuresults.eu/2012-2013.html','http://www.isuresults.eu/2011-2012.html','http://www.isuresults.eu/2010-2011.html','http://www.isuresults.eu/2009-2010.html','http://www.isuresults.eu/2008-2009.html']
with open('homepages.csv', 'r') as f:
    for line in f.readlines():
        #l = line.strip().split(',')
        parenturl.append((line))
for parentUrl in parenturl:
    page = urlopen(parentUrl).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    childUrlList = []
    for anchor in soup.findAll('a', href=True):
        if 'Result' in anchor.text and 'Results' in anchor.text:
            link = anchor['href']
            #fixing spaces in URLS
            link = link.replace(' ','%20')
            #getting only data back to 2008 with typical formatting
            if link[0:4]=='http':
                if link[len(link)-1:len(link)] <>'/':
                    link = str(link)+'/'
                childUrl =  link
                childUrlList.append(childUrl)
                
    #childUrl = 'http://live.isuresults.eu/2015-2016/calgary/'
    grandChildUrlList = []
    for childUrl in childUrlList:    
        page = urlopen(childUrl).read()
        soup = BeautifulSoup(page)
        soup.prettify()

        for anchor in soup.findAll('a', href=True):
            if 'Result' in anchor.text and 'Results' not in anchor.text:
                link = anchor['href']
                grandChildUrl =  urljoin( childUrl, link )
                grandChildUrlList.append(grandChildUrl)

####removing duplicates by making it a set and then a list


    ####get the data
    for site in grandChildUrlList:
        print site
        status = requests.head(site)
        if str(status)=='<Response [200]>':

            numbers = map(int, re.findall(r'\d+', site))
            #Get SiteID
            parsed = urlparse(site)
            siteID =re.sub(r'....-','',parsed.path).replace('/','').replace('.htm','')

            soup = BeautifulSoup(urlopen(site))
            try:
                dataTable = soup.find_all('table')[1]
                headers = [header.text for header in dataTable.find_all('th')]
                headers.insert(0,'SiteID')
                rows = []
                for row in dataTable.find_all('tr'):
                    tds = row.find_all('td')
                    for val in tds:
                        for br in val.find_all('br'): 
                            br.replace_with('|')
                    rows.append([val.text.encode('utf8').replace('\n','').replace('\r','').replace('      ','') for val in row.find_all('td')])
                rows = filter(None,rows)
                rowlength = len(max(rows, key=len))+1
                headers = headers[0:rowlength]
                #with open (str(siteID)+'.csv', 'wb') as f:
                with open (str(siteID)+'.csv', 'wb') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    j = 0
                    for i in rows:
                        writer.writerow([siteID]+rows[j])
                        j+=1


                #######Re order to put time at the end of the file
                reorderedHeaders = headers
                resultsIndex = reorderedHeaders.index('Time:')
                reorderedHeaders += [headers.pop(resultsIndex)]
                with open(str(siteID)+'.csv', 'rb') as infile, open('reordered.csv', 'ab') as outfile:
                    # output dict needs a list for new column ordering
                    writer = csv.DictWriter(outfile, fieldnames=reorderedHeaders)
                    # reorder the header first
                    #writer.writeheader()
                    for row in csv.DictReader(infile):
                        # writes the reordered rows to the new file
                        writer.writerow(row)
                os.remove(str(siteID)+'.csv')

                #######Get the weather and title
                weatherTable = soup.find_all('table')[0]
                weatherData = []
                for row in weatherTable.find_all('tr'):
                    weatherData.append([val.text.encode('utf8').replace('\n','').replace('\r','').replace('      ','').replace('\xe2\x84\x83','C') for val in row.find_all('td')])

                table = soup.find_all('table')[1]
                title = table.caption.get_text()
                title = title.replace('\r','').replace('\t', ''). replace('\n','').replace('                ',',').lstrip()
                title = title.encode('utf8').split(',')
                weatherData.pop(0)
                weatherData = [item for sublist in weatherData for item in sublist]
                weatherData = [siteID.encode('utf8')] +weatherData + title

                with open('Titles.csv', 'ab') as w:
                    writer = csv.writer(w)
                    writer.writerow(weatherData)
            except:
                with open('failedUrls.csv','ab') as fail:
                    writer = csv.writer(fail)
                    writer.writerow([site])
                    print 'failed site '+str(site)
                pass
        else:
            with open('failedUrls.csv','ab') as fail:
                writer = csv.writer(fail)
                writer.writerow(['Doesnt exist,'+site])
                print 'bad site '+str(site)

##Reiterating over the failedSites URL####
##This is a repeat process of what is up above, just going from a different angle###
##I'm sure there is a better way to do this###
print "going through the failed sites"
print "Running through sites that only have one table (no weather data i.e. Sochi)"
failedwebsites = []
brokenlink = 0
###load a list of failed websites
with open('failedurls.csv', 'r') as fails:
    for row in fails:
####Don't grab the 'doesn't exist' ones
        if row[1:2]=='D':
            brokenlink +=1
        else:
            failedwebsites.append(row.replace('\n',''))
print "Non existint websites = %s" % brokenlink

    ####get the data
for site in failedwebsites:
    print site
    status = requests.head(site)
    if str(status)=='<Response [200]>':

        numbers = map(int, re.findall(r'\d+', site))
        #Get siteID will be the site
        siteID =site

        soup = BeautifulSoup(urlopen(site))
        try:
            dataTable = soup.find_all('table')[0]
            headers = [header.text for header in dataTable.find_all('th')]
            headers.insert(0,'SiteID')
            rows = []
            for row in dataTable.find_all('tr'):
                tds = row.find_all('td')
                for val in tds:
                    for br in val.find_all('br'): 
                        br.replace_with('|')
                rows.append([val.text.encode('utf8').replace('\n','').replace('\r','').replace('      ','') for val in row.find_all('td')])
            rows = filter(None,rows)
            rowlength = len(max(rows, key=len))+1
            headers = headers[0:rowlength]
            #with open (str(siteID)+'.csv', 'wb') as f:
            with open ('OneTableURL.csv', 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                j = 0
                for i in rows:
                    writer.writerow([siteID]+rows[j])
                    j+=1


            #######Re order to put time at the end of the file
            reorderedHeaders = headers
            resultsIndex = reorderedHeaders.index('Time:')
            reorderedHeaders += [headers.pop(resultsIndex)]
            with open('OneTableURL.csv', 'rb') as infile, open('reordered.csv', 'ab') as outfile:
                # output dict needs a list for new column ordering
                writer = csv.DictWriter(outfile, fieldnames=reorderedHeaders)
                # reorder the header first
                #writer.writeheader()
                for row in csv.DictReader(infile):
                    # writes the reordered rows to the new file
                    writer.writerow(row)
            os.remove('OneTableURL.csv')



            #######Get the weather and title
            title = dataTable.caption.get_text()
            title = title.replace('\r','').replace('\t', ''). replace('\n','').replace('                ',',').lstrip()
            title = title.encode('utf8').split(',')
            titlerow = [siteID.encode('utf8')] + [title[0]]

            with open('Titles.csv', 'ab') as w:
                writer = csv.writer(w)
                writer.writerow(titlerow)


        except:
            with open('trulyfailedUrls.csv','ab') as fail:
                writer = csv.writer(fail)
                writer.writerow([site])
                print 'failed site '+str(site)
            pass
    else:
        with open('trulyfailedUrls.csv','ab') as fail:
            writer = csv.writer(fail)
            writer.writerow(['Doesnt exist,'+site])
            print 'bad site '+str(site)
import re,csv, tablib, os, sys
from natsort import natsorted

#####Get the first lap time and break out the data so I can tabularize it#####
with open('reordered.csv') as infile, open('newformat.csv', 'wb') as outfile:
    rowreader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, escapechar = ' ')
    for row in rowreader:
       if len(row)>7:
          row[7] = re.sub(r'(\.[0-9][0-9])([0-9][0-9][0-9]m)',r'\1,|\2', row[7])
          row[7] = re.sub(r'(DNF)([0-9])',r'\1,|\2', row[7])
          row[7] = re.sub(r'(DNS)([0-9])',r'\1,|\2', row[7])
          row[7] = re.sub(r'(DQ)([0-9])',r'\1,|\2', row[7])
          row[7] = re.sub(r'([0-9][0-9])(0.5)',r'\1,|\2', row[7])
          row[7] = re.sub(r'(\([0-9]\))(\s+[0-9][0-9][0-9]m)',r'\1,|\2', row[7])
          row[7] = row[7].replace(' ', '').replace('\t','')
          row.append(' ')
          #print row
          writer.writerow(row)

with open ('newformat.csv') as newformat, open ('splitdata.csv', 'wb') as splitData, open ('firstpart.csv','wb') as firstPart:
   newrowreader = csv.reader(newformat, delimiter = ',')
   writer = csv.writer(splitData, delimiter = ',')
   firstwriter = csv.writer(firstPart, quoting=csv.QUOTE_NONE, escapechar = ' ',delimiter = ',')
   i = 0
   for newrow in newrowreader:
      writer.writerow([newrow[8]])
      firstwriter.writerow(newrow[0:8])
      i+=1

splitData.close()
firstPart.close()
print 'done'

f = open('splitdata.csv', 'r')
data = f.read()
       
dictionaries = []
headers = ('100m','200m','300m','400m','500m','600m','700m','800m','1000m','1100m','1200m','1400m','1500m','1600m','1800m','2000m','2400m','2200m','2800m','2600m','3000m','3200m','3400m','3600m','3800m','4000m','4200m','4400m','4600m','4800m','5000m','5200m','5600m','6000m','6400m','6800m','7200m','7600m','8000m','8400m','8800m','9200m','9600m','10000m','0.5','1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0','5.5','6.0','6.5','7.0','7.5','8.0','DQ','DNF')
headers = set(headers)

for row in data.split('\n'):
    row_dict = {}
    for entry in row.split('|'):
        column, value = map(str.strip, entry.partition('-')[::2])
        if column:
            row_dict[column] = value
    dictionaries.append(row_dict)
    #headers.update(row_dict.keys())

#headers = sorted(headers, key=lambda x: int(x[:-1]))
dataset = tablib.Dataset(headers=headers)
for row_dict in dictionaries:
    dataset.append([row_dict.get(header) for header in headers])

stufftowrite = dataset.csv
with open('happydata.csv', 'wb') as happy:
    happy.write(stufftowrite)
f.close()


######Combining lap times back to the racers
print "Combining Racers and Split Data"
with open('firstpart.csv') as FirstFile, open('happydata.csv') as SecondFile, open('Racer.csv', 'wb') as outfile:
    ReaderOne = list(csv.reader(FirstFile))
    ReaderTwo = list(csv.reader(SecondFile))
    writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, escapechar = ' ')
    for row in ReaderOne:
        RowIndex = ReaderOne.index(row)
        try:           
           for field in zip(ReaderTwo[RowIndex]):
               #ColumnIndex = len(row)+1
               ReaderOne[RowIndex].extend((field))#insert(len(row)+1,field)
           writer.writerow(ReaderOne[RowIndex])
        except:
           pass
        else:
           pass
os.remove('happydata.csv')
os.remove('firstpart.csv')
os.remove('newformat.csv')
os.remove('splitdata.csv')
os.remove('reordered.csv')
os.remove('failedUrls.csv')
