import requests
from bs4 import BeautifulSoup
import os                          
import json                         
import csv                         
import time                        
import math                         
from collections import Counter     

tStart = time.time() # 計時開始
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

class AnueClass:
    def __init__(self, global_Bottleneck, global_key_words):
        self.key_words = global_key_words
        self.global_Bottleneck = global_Bottleneck
    def preset(self, index):
        url = r"https://news.cnyes.com/api/v3/search"
        url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        url_params = {'page':'1',
                        'q':self.key_words[index]}
        try:
            r = requests.get(url,headers= url_headers ,params = url_params)
            r.encoding = 'utf-8'
        except requests.exceptions.Timeout as ex:
            print(ex)
        if r.status_code == 200:
            temp =  json.loads(r.text)
            self.page_total = temp["items"]["last_page"] 
            url = r"https://news.cnyes.com/api/v3/search"
            url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            url_params = {'page':self.page_total,
                            'q':self.key_words[index]}
            try:
                r = requests.get(url,headers= url_headers ,params = url_params)
                r.encoding = 'utf-8'
            except requests.exceptions.Timeout as ex:
                print(ex)
            if r.status_code == 200:
                temp =  json.loads(r.text)
                self.count_total = temp["items"]["total"]
                self.last_page_count_front = temp["items"]["from"]
                self.last_page_count_end = temp["items"]["to"]
                self.last_page_count_total = self.last_page_count_end - self.last_page_count_front + 1
            else:
                print("Request Fail.")
        else:
            print("Request Fail.")
    def normal_page_url(self, index):
        for i in range(1, self.page_total+1):
            url = r"https://news.cnyes.com/api/v3/search"
            url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            url_params = {'page':i,
                        'q':self.key_words[index]}
            try:
                r = requests.get(url,headers= url_headers ,params = url_params)
                r.encoding = 'utf-8'
            except requests.exceptions.Timeout as ex:
                print(ex)
            if r.status_code == 200:
                temp =  json.loads(r.text)
                for j in range(0, len(temp["items"]["data"])):
                    search_ID = temp["items"]["data"][j]["newsId"]
                    result = [r'https://news.cnyes.com/news/id/' + str(search_ID)]
                    self.url_list.extend(result)
            else:
                print("Request Fail.")
    def filtering(self):
        self.url_list_filtered = list(set(self.url_list))
    def print_details(self):
        store_list_duplicated = dict(Counter(self.url_list))
        print ("Duplicated URLs：")
        print ({key:value for key,value in store_list_duplicated.items()if value > 1})
    def extracting(self):
        self.bottleneck = self.global_Bottleneck
        #self.total_list = [] 
        self.total_list_2 = []
        self.temp_list = [] 
        for i,find_url in enumerate(self.url_list_filtered):
            url = find_url
            url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            try:
                r = requests.get(url,headers= url_headers)
                r.encoding = 'utf-8'
            except requests.exceptions.Timeout as ex:
                print(ex)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                find_title = soup.find(attrs={"itemprop":"headline"}).text
                temp_time = soup.find("time")['datetime']
                find_time = temp_time[0:10] + " " + temp_time[11:-6]
                temp =  soup.find(attrs={"class":"_1UuP"}).findAll("p")
                find_content = ''
                for j in temp:
                    temp2 = j.text.replace('\n', '')
                    find_content += temp2
                self.temp_list.extend(["Anue"])
                self.temp_list.extend([find_url])
                self.temp_list.extend([find_title])
                self.total_list_2.extend([self.temp_list])
                self.temp_list = []
            else:
                print("Request Fail.")
            self.count_offset += 1
            if self.count_offset >= self.bottleneck:
                break
    def saveAsCsv(self):
        csv_file = "!Temp_Url.csv"
        with open(csv_file, 'a', newline="", encoding="utf-8-sig") as fp:
            writer = csv.writer(fp)
            for i in self.total_list_2:
                writer.writerow(i)
            print("File create complete.")
    def start(self):
        self.url_list = []
        self.url_list_filtered = []
        self.total_list = []
        self.total_list_2 = []
        self.temp_list = []
        for index, keyword in enumerate(self.key_words):
            self.bottleneck = self.global_Bottleneck
            self.page_total = 0 
            self.count_total = 0 
            self.count_offset = 0 
            self.last_page_count_front = 0
            self.last_page_count_end = 0
            self.last_page_count_total = 0
            self.preset(index)
            if self.bottleneck > self.count_total:
                self.bottleneck = self.count_total
            elif self.bottleneck <= 0:
                self.bottleneck = 1
            temp_page_total = math.ceil(self.bottleneck / 20)
            if temp_page_total != self.page_total and temp_page_total < self.page_total:
                self.page_total = temp_page_total
                self.last_page_count_total = self.bottleneck % 20
            self.normal_page_url(index) 
        self.filtering()
        self.print_details()
        self.extracting()
        self.saveAsCsv()
        tEnd = time.time()
        print ("It cost %f sec" % (tEnd - tStart))

def setup(global_Bottleneck, global_key_words):
    A = AnueClass(global_Bottleneck, global_key_words)
    A.start()
