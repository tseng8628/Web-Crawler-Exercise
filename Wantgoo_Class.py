import requests
from bs4 import BeautifulSoup
import os                           # 用來設定環境變數，以便執行本py檔案
import json                         # 有Api都會用到
import csv                          # 操作csv檔
# import codecs                     #
# from urllib.parse import unquote  # 解碼 ASCII碼
import time                         # 計時用
# import math                       # counting total page
# from collections import Counter   # 計算陣列重複數
# from collections import defaultdict # 計算陣列重複數
import re                           # remove html tag
# import sys                        # 用來設定環境變數，以便import其他py檔案

tStart = time.time() # 計時開始
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

# ---------------------------Class define---------------------------------------------------------------------
class WantgooClass:
    def __init__(self, global_Bottleneck, global_key_words):
        self.key_words = global_key_words
        self.global_Bottleneck = global_Bottleneck

    # -------------------------------Gaining URLs---------------------------------------------------
    def normal_page_url(self):
        self.count_offset = 0
        while self.count_offset < self.bottleneck:
            self.page_total += 1
            url = r'https://www.wantgoo.com/news/list/category'
            url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            url_params = {'Title':'頭條',
                                'PageNo':self.page_total}

            try:
                r = requests.get(url, headers= url_headers, params = url_params)
                r.encoding = 'utf-8'
            except requests.exceptions.Timeout as ex:
                print(ex)

            if r.status_code == 200:
                soup =  BeautifulSoup(r.text, "lxml")

                title_list_check = soup.find(attrs={'class': 'sort-list'}).text.replace("\n","")
                title_temp_array = soup.find(attrs={'class': 'sort-list'}).findAll('a') # 全部的title，EX:<a href="/news/content/index?ID=1017760">日本9月工具機訂單年減35%  連12個月呈現衰退</a>
                
                # 如果已經到最後一頁的下一頁，則class : sort-list底下會只剩一個\n，即跳出迴圈
                if title_list_check == "":
                    break

                for raw_title in title_temp_array:
                    title_temp_single = raw_title.text  # 每次取出一個title，並提取裡面的文字，用來跟keywords做比對
                    for word in self.key_words:
                        if word in title_temp_single:
                            search_ID = raw_title.get("href")[-7:]  # 跟keywords做比對相符，即提取裡面的Url ID
                            result = [r'https://www.wantgoo.com/news/content/index?ID=' + str(search_ID)]      # store as a list[]

                            self.url_list.extend(result)
                            
                            self.count_offset += 1
                            if self.count_offset >= self.bottleneck:
                                break
                print("Page " + str(self.page_total) + "'s URL retrieve complete.")

            else:
                print("Request Fail.")

    # ------------------------------------------------Debug-------------------------------------------------
    #def print_details(self):
        #for i,j in enumerate(self.url_list):
        #    print(str(i+1) + "：" + str(j))

    # ---------------------------Extracting Context--------------------------------------------------------
    def extracting(self):
        #self.total_list = []
        self.total_list_2 = []
        self.temp_list = []

        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        for i,find_url in enumerate(self.url_list):
            url = find_url
            url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

            try:
                r = requests.get(url,headers= url_headers) # params = url_params
                r.encoding = 'utf-8'
            except requests.exceptions.Timeout as ex:
                print(ex)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")

                # <h1 id="heading">半導體原料的前車之鑑 南韓石化業加速開發電動車先進材料</h1>
                find_title = soup.find('h1', {'id': 'heading'}).text

                # <time>2019-10-09 17:10</time>
                temp_time = soup.find('div', {'class': 'orgin'}).find('time')
                find_time = temp_time.text

                # <div class="content" style="">韓媒報導<br><br></div>
                find_content = soup.find('div', {'class': 'content'}).text.replace('\n', '')
                find_content = cleanhtml(find_content)

                self.temp_list.extend(["Wantgoo"])
                self.temp_list.extend([find_url])
                self.temp_list.extend([find_title])
                self.total_list_2.extend([self.temp_list])
                self.temp_list = []

                print("Num " + str(i+1) + " Search complete. Html: " + str(find_url))
            else:
                print("Request Fail.")

    # ---------------------------Output---------------------------------------------------------------------
    def saveAsCsv(self):
        csv_file = "!Temp_Url.csv"
        with open(csv_file, 'a', newline="", encoding="utf-8-sig") as fp:
            writer = csv.writer(fp)
            for i in self.total_list_2:
                writer.writerow(i)
            print("File create complete.")

    # ----------------------------------- Commence ---------------------------------------------------------
    def start(self):
        # --------------------------------
        # pre-set
        # 完全透過網頁DOM拿取資料
        # 因為不能事先拿到 page_total，所以必須用while迴圈慢慢跑完，結束時最後一頁會沒有資料，code會自動跳出迴圈 (所以也不需要寫preset() )
        # 另外因為不能用網站內建的關鍵字搜尋(只能最多搜尋100筆)，所以必須把每筆Title拿來做字串比對，有比對到就放進total_list[]陣列裡等待輸出

        # 簡易說明
        # 資料全部網頁
        # 一次抓一個區間的資料 20、40、60等等，但是會抓到很多不是符合關鍵字的資料，因此每頁大概頂多5筆符合
        # --------------------------------
        self.url_list = []           # store url (dynamic extend)
        #url_list_filtered = [] # deleted duplicate url_list
        self.total_list = []         # store all of items' url title、time、context (dynamic extend)
        self.total_list_2 = []       # saving url、title
        self.temp_list = []          # store one item's url title、time、context (dynamic change)

        self.bottleneck = self.global_Bottleneck# goal count (dynamic)
        self.page_total = 0                  # total request page
        self.count_total = 0                 # total count
        self.count_offset = 0                # current count

        # set url_list      (dynamic)
        self.normal_page_url()

        # Print All Urls
        ## print_details()

        # set count_offset  (dynamic)
        # set total_list
        # set temp_list
        self.extracting()

        # set File as .csv
        self.saveAsCsv()

        # ---------------------------Time---------------------------------------------------------------------
        tEnd = time.time() # 計時結束
        print ("It cost %f sec" % (tEnd - tStart))

def setup(global_Bottleneck, global_key_words):
    A = WantgooClass(global_Bottleneck, global_key_words)
    A.start()
