from selenium import webdriver
from selenium.webdriver.common.by import By
import configparser
import time
from urllib.request import urlretrieve
from datetime import datetime
import slack

# absolute path of config.ini
config_url = "/home/sysadm/mondrian_menu_uploader/config.ini"
TIMEOUT_MAX_COUNT = 10

class WebCrawler:
    def __init__(self):
        # prev number
        self.config = configparser.ConfigParser()
        self.config.read(config_url, encoding="utf8")
        self.whitelist = [".", " "]

        self.number = int(self.config["info"]["number"])
        self.target = self.config["info"]["target"]
        self.main_url = self.config["info"]["main_url"]
        self.img_folder = self.config["info"]["img_folder"]

        self.token = self.config["slack"]["token"]
        self.channel = self.config["slack"]["channel"]

        print("initialization finished, number =", self.number)

    def crawl(self):
        options = webdriver.ChromeOptions()

        options.add_argument("--headless")
        options.add_argument("--single-process")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(self.target, options=options)
        driver.get(f"{self.main_url}/posts")

        class_list = []
        addr_list = []
        time.sleep(1)
        timeout_count = 0
        while 1:
            if timeout_count >= TIMEOUT_MAX_COUNT :
                return
            class_list = driver.find_elements(by=By.CLASS_NAME, value="wrap_post")
            if len(class_list) == 0:
                time.sleep(1)
                print("loading...")
                timeout_count += 1
                continue
            else:
                break

        for i in class_list:
            try:
                temp = i.find_element(by=By.TAG_NAME, value="a")
                addr_list.append(temp.get_attribute("href"))
            except:
                continue
        
        final_number = 0
        for addr in addr_list:
            temp_num = int(addr.split(f"{self.main_url}/")[1])
            if temp_num > self.number:
                print(f"number: {temp_num}")
                driver.get(addr)
                time.sleep(2)
                title = driver.find_element(by=By.CLASS_NAME, value="tit_post").text
                print(f"title: {title}")
                if title == "":
                    continue
                if (title.find("중식메뉴") != -1):
                    url = driver.find_elements(by=By.CLASS_NAME, value="wrap_thumb")
                    # logo / menu / logo
                    if len(url) != 3:
                        continue
                    else:
                        url2 = url[1].find_element(by=By.TAG_NAME, value="img")
                        url3 = url2.get_attribute("src")
                        day = datetime.today().strftime("%m월%d일")
                        print(f"filename: {day}")
                        urlretrieve(url3, (f"{self.img_folder}/{day}.jpg"))
                        self.files_upload(f"{day}.jpg")
                        if final_number == 0:
                            final_number = temp_num
                        break

        self.config["info"]["number"] = str(final_number)
        if final_number != 0:
            with open(config_url, "wt", encoding="utf8") as conf_file:
                self.config.write(conf_file)

    # def post_message(self, message):
    #     client = slack.WebClient(token=self.token)
    #     response = client.chat_postMessage(
    #         channel=self.channel,
    #         text=message
    #     )
    def files_upload(self, filename):
        client = slack.WebClient(token=self.token)
        response = client.files_upload(
            channels=self.channel,
            file=(f"{self.img_folder}/{filename}"),
            title=filename,
            filetype="jpg",
        )
crawler = WebCrawler()
crawler.crawl()
print(time.strftime("%c", time.localtime(time.time())))
print('-----------------------------')
