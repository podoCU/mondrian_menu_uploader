from selenium.webdriver.common.by import By
import configparser
import time
import slack


class WebCrawler:
    def __init__(self):
        # prev number
        self.config = configparser.ConfigParser()
        self.config.read("/home/sysadm/mondrian_menu_uploader/config.ini", encoding="utf8")

        self.number = int(self.config["info"]["number"])
        self.img_folder = self.config["info"]["img_folder"]

        self.token = self.config["slack"]["token"]
        self.channel = self.config["slack"]["channel"]

        print("emergency upload finished, number =", self.number)

    def upload(self, filename):
        client = slack.WebClient(token=self.token)
        response = client.files_upload(
            channels=self.channel,
            file=self.img_folder + "/" + filename,
            title=filename,
            filetype="jpg",
        )
#비상 업로드
image_name = '1206.jpg'
crawler = WebCrawler()
crawler.upload(image_name)
print(time.strftime("%c", time.localtime(time.time())))
print("------------------------------")
