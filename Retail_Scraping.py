#!/usr/bin/env python
# coding: utf-8

# In[30]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome(executable_path=r"C:\Users\ipe77\Documents\Master Data Science\05 Tipologia\chromedriver.exe")
browser.get('https://www.gadisline.com')

#option_text='15002'
#browser.find_element_by_xpath("//select[@class='select2-search__field']/option[text()='option_text']").click()


# In[18]:


import urllib.request
from urllib.request import urlopen, Request
#datos = urllib.request.urlopen("https://www.gadisline.com/").read().decode()
#from bs4 import BeautifulSoup
#soup =  BeautifulSoup(datos)
#tags = soup("a")
#for tag in tags:
#	print(tag.get("href"))

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
reg_url = "https://www.gadisline.com/inicio/"
req = Request(url=reg_url, headers=headers) 
html = urlopen(req).read().decode()
from bs4 import BeautifulSoup
soup =  BeautifulSoup(html)
tags = soup("a")
for tag in tags:
	print(tag.get("href"))

