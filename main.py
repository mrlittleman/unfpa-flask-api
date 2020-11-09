
import re
from bs4 import BeautifulSoup as bs
import requests
from datetime import date
from lxml import html, etree
import pdb
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from firebase import firebase
from flask import Flask, jsonify
from collections import OrderedDict as od
firebase = firebase.FirebaseApplication("https://unfpa-289210.firebaseio.com/", '')
app = Flask(__name__)
app.config["DEBUG"] = True

#getting data from googlesheets
def get_keys_from_sheets():
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'keysheet.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(credentials)
    sheet = client.open('keywords').sheet1
    col = sheet.col_values(1)
    return(col)


def fetch_url(url):
    headers_Get = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
    }
    return requests.get(url, headers=headers_Get)

#Scrape data from google search engine
def link_scraper():
    keywords =  get_keys_from_sheets()
    link_list = []
    for keyword in keywords:
        response = fetch_url('https://www.google.com/search?q={}'.format(keyword))
        raw = response.text
        tree = html.fromstring(raw)
        els = tree.xpath('//div[@class="rc"]//div[@class="yuRUbf"]')
        for el in els:
            link_list.append(el.find('a').attrib['href'])
        return link_list

#open each sites and count its keyword content
def key_word_counts():
    keywords = get_keys_from_sheets()
    data =  link_scraper()
    keyword_counts = []
    for data_gathered in data:
        url = fetch_url(data_gathered)
        for keys in keywords:
            search = re.findall('{}'.format(keys), url.text)
            if (len(search) != 0):
                keyword_counts.append(len(search))
    return keyword_counts

#get used keywords
def used_keywords():
    keywords = get_keys_from_sheets()
    data =  link_scraper()
    keyword_used = []
    for data_gathered in data:
        url = fetch_url(data_gathered)
        for keys in keywords:
            search = re.findall('{}'.format(keys), url.text)
            if (len(search) != 0):
                keyword_used.append(keys)
    return keyword_used



'''
def keywords_and_keycounts_entry():
    keywords = used_keywords()
    key_counts = key_word_counts()
    keywords_and_key_counts = []
    
    for counts in key_counts:
        for keys in keywords:
            if counts and keys not in  keywords_and_key_counts:
                keywords_and_counts_data = {
                    'keyword_counts': counts,
                    'keywords': keys
                }
                keywords_and_key_counts.append(keywords_and_counts_data)
    result_keys = firebase.post('/keywords_and_keycounts_entry',keywords_and_key_counts)
    return result_keys

#store data gathered
def websites_dates_entry():
    links = link_scraper()
    date_scrape = date.today()
    links_and_dates = []
    for link in links:
        links_and_dates_data = {
            'websites': link,
            'date': date_scrape.strftime('%d/%m/%y')
        }
        links_and_dates.append(links_and_dates_data)
    result_web = firebase.post('/websites_dates_entry',links_and_dates)   
    return result_web
'''



@app.route('/', methods=['GET'])
def get_data():
    result_web = firebase.get('/keywords_and_keycounts_entry','')
    return jsonify(result_web)

@app.route('/websites_dates_entry', methods=['GET'])
def get_dat():
    result_web = firebase.get('/websites_dates_entry','')
    return jsonify(result_web)

if __name__ == '__main__':
   app.run()

