from selenium import webdriver
from selenium.webdriver.common.by import By
import configparser
import time
from urllib.request import urlretrieve
import slack

# absolute path of config.ini
config_url = "/home/sysadm/mondrian_menu_uploader/config.ini"


class WebCrawler:
    def __init__(self):
        # prev number
        self.config = configparser.ConfigParser()
        self.config.read(config_url, encoding="utf8")
        self.whitelist = [".", " "]

        self.number = int(self.config["info"]["number"])
        self.target = self.config["info"]["target"]
        self.main_url = self.config["info"]["main_url"]
        self.url_token = self.main_url.split("pf.kakao.com/")[1]
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
        driver.get(self.main_url)

        class_list = []
        addr_list = []
        time.sleep(1)
        while 1:
            class_list = driver.find_elements(by=By.CLASS_NAME, value="box_list_board")
            if len(class_list) == 0:
                time.sleep(1)
                print("loading...")
                continue
            else:
                break

        for i in class_list:
            try:
                temp = i.find_element(by=By.TAG_NAME, value="a")
                addr_list.append(temp.get_attribute("href"))
            except:

                continue

        temp = 1
        i = 0
        while 1:
            if addr_list[i] == temp:
                addr_list.pop(i)
                i -= 1
            temp = addr_list[i]
            if i == len(addr_list) - 1:
                break
            i += 1
        final_number = 0
        for i in addr_list:
            temp_num = i.split(self.url_token + '/')[1]

            if int(temp_num) > self.number:
                driver.get(self.main_url + "/" + temp_num)
                time.sleep(2)
                text = driver.find_element(by=By.CLASS_NAME, value="tit_post").text
                if text == "":
                    text = driver.find_element(by=By.CLASS_NAME, value="desc_post").text

                print(text)
                if (text.find("월") != -1) and (text.find("일") != -1) and (text.find("토") == -1) and (text.find("점심") != -1):
                    text = text.split("일")[0] + "일"
                    for j in self.whitelist:
                        text = text.replace(j, "")
                    print(i, text)
                    url = driver.find_elements(by=By.CLASS_NAME, value="wrap_thumb")
                    url2 = url[1].find_element(by=By.TAG_NAME, value="img")
                    url3 = url2.get_attribute("src")
                    urlretrieve(url3, (self.img_folder + "/" + text + ".jpg"))
                    self.upload(text + ".jpg")
                    if final_number == 0:
                        final_number = temp_num
                    break

        self.config["info"]["number"] = str(final_number)
        if final_number != 0:
            with open(config_url, "wt", encoding="utf8") as conf_file:
                self.config.write(conf_file)
        print(final_number)

    def upload(self, filename):
        client = slack.WebClient(token=self.token)
        response = client.files_upload(
            channels=self.channel,
            file=self.img_folder + "/" + filename,
            title=filename,
            filetype="jpg",
        )

crawler = WebCrawler()
crawler.crawl()
print(time.strftime("%c", time.localtime(time.time())))
print('-----------------------------')
