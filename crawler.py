from selenium import webdriver
from selenium.webdriver.common.by import By
import configparser
import time
import re
from urllib.request import urlretrieve
import slack

class WebCrawler:
    def __init__(self):
        #prev number
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf8')
        self.whitelist = ['.',' ']

        self.number = int(self.config['info']['number'])
        self.target = self.config['info']['target']
        self.main_url = self.config['info']['main_url']
        self.img_folder = self.config['info']['img_folder']

        self.token = self.config['slack']['token']
        self.channel = self.config['slack']['channel']

    def crawl(self):
        options = webdriver.ChromeOptions()

        options.add_argument('headless')
        options.add_argument('disable-gpu')
    
        driver = webdriver.Chrome(self.target, options=options)
        driver.get(self.main_url)
        
        class_list = []
        addr_list = []
        time.sleep(1)
        while(1):
            class_list = driver.find_elements(by=By.CLASS_NAME, value='wrap_thumb')
            if len(class_list)==0:
                time.sleep(1)
                print('loading...')
                continue
            else:
                break

        for i in class_list:
            try:
                #print(class_list[i].find_element(by=By.TAG_NAME, value='a'))
                temp = i.find_element(by=By.TAG_NAME, value='a')
                addr_list.append(temp.get_attribute('href'))
                #print(temp.get_attribute('href'))
            except:
            
                continue
        
        temp = 1
        i=0
        while(1):
            if addr_list[i] == temp:
                addr_list.pop(i)
                i -= 1
            temp = addr_list[i]
            if i == len(addr_list)-1:
                break
            i += 1
        final_number = 0
        temp_text=''
        for i in addr_list:
            temp_num = i.split("_Hvxbis/")[1]
            
            if int(temp_num) > self.number:
                driver.get(self.main_url + '/' + temp_num)
                time.sleep(1)
                text = driver.find_element(by=By.CLASS_NAME, value='tit_post').text
                if text == '':
                    text = driver.find_element(by=By.CLASS_NAME, value='desc_post').text
                result = re.match('\d{1,2}월\D*\d{1,2}일', text)
                if result != None:
                    text = result.group()
                    for j in self.whitelist:
                        text = text.replace(j, '')
                    print(i, text)
                    url = driver.find_elements(by=By.CLASS_NAME, value='wrap_thumb')
                    url2 = url[1].find_element(by=By.TAG_NAME, value='img')
                    url3 = url2.get_attribute('src')
                    urlretrieve(url3, (self.img_folder+'/'+text+'.jpg'))
                    print(url3)

                    #처음일떄 컨티뉴
                    if temp_text == '':
                        temp_text = text
                        final_number = temp_num
                        continue
                    if temp_text == text:
                        self.upload(text+'.jpg')
                        break
                    if temp_text != text:
                        self.upload(temp_text+'.jpg')
                        break
        self.config['info']['number'] = final_number
        with open('config.ini','wt',encoding='utf8') as conf_file:
            self.config.write(conf_file)

    def upload(self, filename):
        client = slack.WebClient(token=self.token)
        response = client.files_upload(
            channels=self.channel,
            file = self.img_folder+'/'+filename,
            title=filename,
            filetype='jpg'
            )

crawler = WebCrawler()
crawler.crawl()

