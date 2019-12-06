from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import io
import sys
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import requests
from urllib.request import Request, urlopen
import json

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

search = input("검색어를 입력하시라요~ : ")
search = urllib.parse.quote(search)
url = "http://www.instagram.com/explore/tags/"+str(search)+"/"

driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.get(url)
sleep(5)

scroll_parse_time = 1.0
reallink = []

while True:
    pageString = driver.page_source
    bs0bj = BeautifulSoup(pageString, "lxml")

    for link1 in bs0bj.find_all(name="div",attrs={"class":"Nnq7C weEfm"}):
        title = link1.select('a')[0]
        real = title.attrs['href']
        reallink.append(real)
        title = link1.select('a')[1]
        real = title.attrs['href']
        reallink.append(real)
        title = link1.select('a')[2]
        real = title.attrs['href']
        reallink.append(real)

    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(scroll_parse_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_parse_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        else:
            last_height = new_height
            continue

csvtext=[]

for i in range(0, len(reallink)):
    csvtext.append([])
    req = Request('http://www.instagram.com/p' +reallink[i], headers={'User-Agent': 'Mozilla/5.0'})

    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "lxml", from_encoding='utf-8')


    try:
        soup0 = json.loads(soup.find('script', type='application/ld+json').text)
        reallink0 = soup0["uploadDate"]
        reallink0 = reallink0[:10]
    except AttributeError:
        reallink0 = "Null"

    csvtext[i].append(reallink0)

    soup1 = soup.find("meta",attrs={"property":"og:description"})
    reallink1 = soup1['content']
    reallink1 = reallink1[reallink1.find("@")+1:reallink1.find(")")]
    reallink1 = reallink1[:20]
    if reallink1 =="":
        reallink1 = "Null"
    csvtext[i].append(reallink1)
    print(csvtext)
    for reallink2 in soup.find_all("meta",attrs={"property":"instapp:hashtags"}):
        reallink2 = reallink2['content']
        csvtext[i].append(reallink2)

data = pd.DataFrame(csvtext)
data.to_excel('insta.xlsx', encoding = 'utf-8')

# elem = driver.find_element_by_tag_name("body")
# text_list =[]
# pagedowns = 1
# while pagedowns < 30:
#     elem.send_keys(Keys.PAGE_DOWN)
#     sleep(1)
#     txt = driver.find_elements_by_xpath('//div/p[@class="txtBody"]')
#     for i in txt:
#         if not i.text in text_list:
#             text_list.append(i.text)
#     pagedowns += 1
#
# print(text_list)
# print(len(text_list))
# driver.quit()
