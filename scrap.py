from bs4 import BeautifulSoup
import requests
import re
import datetime
import json
import os
import validators
from dateutil import parser
from dateutil import tz
from github import Github


def FindUrl(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url]

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

def GetClubhouse(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    
    # title 
    title = soup.find("meta",  property="og:title")["content"]
    
    # event url 
    url = soup.find("meta",  property="og:url")["content"]
    
    # date
    PACIFIC = tz.gettz('America/Los_Angeles')
    to_zone = tz.gettz('Europe/Warsaw')
    timezone_info = {"PST": PACIFIC, "PDT": PACIFIC}
    date = soup.find('div', class_='text-gray-600 text-md')
    date = re.sub(' +', ' ', date.text.replace('\n',''))
    date = parser.parse(date, tzinfos=timezone_info)
    date = date.astimezone(to_zone)
    
    # speakers name
    speakers = soup.find('div', class_='px-6 mt-2 italic font-light text-black text-md')
    speakers = [x.strip() for x in speakers.text.replace('w/','').split(',')]
    
    # avatars
    results = soup.find_all('div', class_='flex items-center justify-center')
    avatar_img_urls = FindUrl(str(results))
    
    # description
    description = soup.select("div[class='mt-6']")[0].text.strip()

    event = {"title": title, "url": url, "date" : date.isoformat(), "speakers" : speakers, "avatars" : avatar_img_urls, "description" : description}
    
    return event


# main ;-)

urls = []

g = Github(os.getenv('GITHUB_TOKEN'))

repo = g.get_repo("kaluzaaa/clubhouse-calendar")
open_issues = repo.get_issues(state='open')
for issue in open_issues:
    if validators.url(issue.title):
        urls.append(issue.title)

urls = list(dict.fromkeys(urls))

events = []

for url in urls:
    events.append(GetClubhouse(url))

with open('_data/events.json', 'w') as outfile:
    json.dump(events, outfile, ensure_ascii=False, indent=2)