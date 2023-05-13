import telebot
import time
from telebot import types 
from config import token
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time 
import urllib
import os

bot = telebot.TeleBot(token)

def set_driver(path):
    options = webdriver.ChromeOptions()
    # user-agent
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
    # disable webdriver mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    return webdriver.Chrome(service=Service(path), options=options) 

def get_img(driver, id, ind):
    img = driver.find_elements(By.TAG_NAME, 'img')[ind + 2]
    src = img.get_attribute("src")
    print("Source found...")
    urllib.request.urlretrieve(src, f"{id}{ind}.png")
    print("Image downloaded.")

def get_video(driver, id, ind):
    vid = driver.find_elements(By.TAG_NAME, 'video')[ind]
    src = vid.get_attribute("src")
    print("Source found...")
    urllib.request.urlretrieve(src, f"{id}{ind}.mp4")
    print("Video downloaded.")

def valid_url(url):
    return 'instagram.com/p/' in url

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет друг! Тебя приветствует igsaver bot. Мой функционал заключается в скачивании контента с instagram. Для работы со мной присылай мне ссылку на пост, контент с которого хочешь скачать.")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    driver = set_driver('chromedriver.exe')
    id = message.from_user.id
    text = message.text
    if not valid_url(text):
        bot.send_message(id, "Некорректный url, попробуйте заново!")
        return
    bot.send_message(id, "URL принят и обрабатывается...")
    filenames = []
    try:
        driver.get(text)
        time.sleep(5)
        images, videos = 0, 0
        mediafiles = []
        while True:
            try:
                get_video(driver, id, videos)
                video = open(f"{id}{videos}.mp4", "rb")
                mediafiles.append([types.InputMediaVideo(video), video])
                filenames.append(f"{id}{videos}.mp4")
                time.sleep(2.5)
                videos += 1
            except Exception as E:
                get_img(driver, id, images)
                image = open(f"{id}{images}.png", "rb")
                mediafiles.append([types.InputMediaPhoto(image), image])
                filenames.append(f"{id}{images}.png")
                time.sleep(1.5)
                images += 1
            try:
                btn = driver.find_element(By.CSS_SELECTOR, "[aria-label='Далее']").click()
            except Exception as E:
                print(E)
                break
        bot.send_media_group(id, [mediafile[0] for mediafile in mediafiles])
        # Closing files after sending message.
        for mediafile in mediafiles:
            mediafile[1].close()
    except Exception as e:
        print(e)
        bot.send_message(id, "Упс, что-то пошло не так. Попробуйте заново!")
    finally:
        driver.close()
        driver.quit()
        # Cleaning
        for filename in filenames:
            os.remove(filename)

bot.polling(none_stop=True, interval=0)