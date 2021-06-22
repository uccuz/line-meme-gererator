from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage,ImageSendMessage,
    TemplateSendMessage, MessageTemplateAction, PostbackTemplateAction, ButtonsTemplate
)

from bs4 import BeautifulSoup as bs 
import requests
import random
from datetime import timedelta

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

topic_dic = {}

def random_meme():
    url = 'https://memes.tw/wtf'
    header = {'User-Agent': 'Custom'}
    page_num = random.randint(1, 10)
    img_num = random.randint(0, 9)
    payload = {'page': page_num}
    img = bs(requests.get(url,headers = header, params = payload).text ,"lxml").find_all(class_='img-fluid')[img_num]['data-src']
    return img

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

@handler.add(PostbackEvent)
def handle_post_message(event):
    user_id = event.source.user_id
    data = event.postback.data
    topic_dic[user_id] = data
    line_bot_api.reply_message(
          event.reply_token,
          TextMessage(
              text = "選擇主題成功，請點選主題迷因按鈕來互動"
          )
        )


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "熱門迷因":
        img_url = random_meme()
        reply_msg = ImageSendMessage(
            original_content_url = img_url,
            preview_image_url = img_url
            )
        line_bot_api.reply_message(event.reply_token, reply_msg)
    elif event.message.text == "主題選擇":
        topic, img_url, describe, url = random_channel()
        reply_msg = TemplateSendMessage(
            alt_text='迷因主題',
            template = ButtonsTemplate(
              title = topic,
              text = describe,
              thumbnail_image_url = img_url,
              actions=[
                  PostbackTemplateAction(
                      label='選擇主題',
                      text= '選擇主題 ' + topic,
                      data = url
                  ),
                  MessageTemplateAction(
                      label='換個主題',
                      text='主題選擇'
                  )
              ]
          )
        )
        line_bot_api.reply_message(event.reply_token, reply_msg)
    elif event.message.text == "主題迷因":
        user_id = event.source.user_id
        if user_id in topic_dic:
            img_url = random_channel_meme(int(topic_dic[user_id]))
            reply_msg = ImageSendMessage(
                original_content_url = img_url,
                preview_image_url = img_url
                )
        else:
          reply_msg = TextSendMessage("你還沒選擇主題喔!")
        line_bot_api.reply_message(event.reply_token, reply_msg)
    
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)