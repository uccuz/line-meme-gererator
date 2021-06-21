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

#topic, img_url, describe, url = random_channel()

def random_channel_meme(channel_id):
    url = 'https://memes.tw/wtf'
    header = {'User-Agent': 'Custom'}
    page_num = random.randint(1, 5)
    payload = {'page': page_num, 'contest': channel_id}
    while page_num >= 1:
        payload['page'] = page_num
        web_data = bs(requests.get(url,headers = header, params = payload).text ,"lxml")
        if web_data.find(class_='img-fluid') != None:
            break
        else:
            page_num = (page_num/2)
    content = web_data.find_all(class_='img-fluid')
    img_num = random.randint(0, len(content)-1)
    img = content[img_num]['data-src']
    return img

#random_channel_meme(1780)
print(random_channel_meme(6))