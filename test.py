from bs4 import BeautifulSoup as bs 
import requests
import random

def random_channel():
    url = 'https://memes.tw/wtf/contests'
    header = {'User-Agent': 'Custom'}
    page_num = random.randint(1, 5)
    img_num = random.randint(0, 19)
    payload = {'page': page_num}
    content = bs(requests.get(url,headers = header, params = payload).text ,"lxml").find_all(class_='mb-4')
    topic  = content[img_num].find(class_='text-black').text
    img_url = content[img_num].find(class_='img-fluid')['src']
    describe = content[img_num].find(class_='text-muted text-center').text.replace(" ", "").replace("\n", "")
    url  = content[img_num].find(class_='text-black')['href'].replace("/wtf?contest=", "")
    return topic, img_url, describe, url

topic, img_url, describe, url = random_channel()

print(topic)
print(img_url)
print(describe)
print(url)