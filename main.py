import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QHeaderView

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pyperclip
import time
import datetime

from ui import Ui_MainWindow


def find(chrome, css):
    wait = WebDriverWait(chrome, 5)
    return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))


def find_all(chrome, css):
    find(chrome, css)
    return chrome.find_elements(By.CSS_SELECTOR, css)


mails = []


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # selenium up
        chrome = webdriver.Chrome()
        self.chrome = chrome

        # naver login
        chrome.get("https://mail.naver.com")
        input_id = find(chrome, "#id")
        input_pw = find(chrome, "#pw")

        pyperclip.copy("네이버 아이디 입력")
        time.sleep(1)
        input_id.click()
        input_id.send_keys(Keys.CONTROL, "v")

        pyperclip.copy("네이버 비밀번호 입력")
        time.sleep(1)
        input_pw.click()
        input_pw.send_keys(Keys.CONTROL, "v")
        input_pw.send_keys("\n")

        # 네이버 메일
        for mail in find_all(chrome, "ul.mail_list li"):
            date = mail.find_element(
                By.CSS_SELECTOR, "div.mail_date_wrap span.mail_date").text

            # 오늘인 경우
            now = datetime.datetime.now()
            if len(date) < 9:
                date = f"{now.year}.{now.month}.{now.day} {date.split()[1]}"
            # 이변 년도인 경우
            elif len(date) < 12:
                date = f"{now.year}.{date}"
            date = datetime.datetime.strptime(date, "%Y.%m.%d %H:%M")
            site = "네이버"
            sender = mail.find_element(
                By.CSS_SELECTOR, ".mail_sender button.button_sender").text[6:]

            try:
                mail.find_element(
                    By.CSS_SELECTOR, "div.mail_title em.icon_attachments").text
                attached = True
            except:
                attached = False

            title = mail.find_element(
                By.CSS_SELECTOR, "div.mail_title span.text").text
            link = mail.find_element(
                By.CSS_SELECTOR, "div.mail_title > a").get_attribute("href")

            mails.append({
                "date": date,
                "site": site,
                "sender": sender,
                "attached": attached,
                "title": title,
                "link": link
            })

        # 다음 메일
        chrome.get(
            "https://logins.daum.net/accounts/ksso.do?url=https%3A%2F%2Fwww.daum.net")
        input_id = find(chrome, "input[name=loginId]")
        input_pw = find(chrome, "input[name=password]")

        input_id.send_keys("다음 아이디 입력")

        input_pw.send_keys("다음 비밀번호 입력")
        input_pw.send_keys("\n")

        chrome.get("https://mail.daum.net/")

        time.sleep(3)

        for mail in find_all(chrome, "ul.list_mail li.mail_item"):
            date = mail.find_element(
                By.CSS_SELECTOR, "span.txt_date").text
            now = datetime.datetime.now()
            if len(date) < 6:
                date = f"{now.year}.{now.month}.{now.day} {date}"
            else:
                date = f"20{date}"

            date = datetime.datetime.strptime(date, "%Y.%m.%d %H:%M")

            site = "다음"
            sender = mail.find_element(
                By.CSS_SELECTOR, "div.info_from > a").text
            try:
                mail.find_element(
                    By.CSS_SELECTOR, "div.info_mail span.img_mail_v1.ico_file2")
                attached = True
            except:
                attached = False
            title = mail.find_element(
                By.CSS_SELECTOR, "div.info_subject a > strong.tit_subject").text
            link = mail.find_element(
                By.CSS_SELECTOR, "div.info_subject a.link_subject").get_attribute("href")

            mails.append({
                "date": date,
                "site": site,
                "sender": sender,
                "attached": attached,
                "title": title,
                "link": link
            })

        # table show

        self.ui.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.ui.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeToContents)
        self.ui.table.setRowCount(len(mails))
        for row, mail in enumerate(mails):
            self.ui.table.setItem(row, 0, QTableWidgetItem(str(mail["date"])))
            self.ui.table.setItem(row, 1, QTableWidgetItem(mail["site"]))
            self.ui.table.setItem(row, 2, QTableWidgetItem(mail["sender"]))
            self.ui.table.setItem(
                row, 3, QTableWidgetItem(str(mail["attached"])))
            self.ui.table.setItem(row, 4, QTableWidgetItem(mail["title"]))

        self.ui.table.cellDoubleClicked.connect(self.open_mail)

    def open_mail(self, r, c):
        mail = mails[r]
        link = mail["link"]

        self.chrome.get(link)

        self.ui.lb_title.setText(mail["title"])
        if mail["site"] == "네이버":
            content = find(self.chrome, "div.mail_view_contents_inner").text
        else:
            content = find(
                self.chrome, "div.viewer_body > div.txt_mailview").text

        self.ui.lb_content.setText(content)


if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    sys.exit(app.exec()).text
