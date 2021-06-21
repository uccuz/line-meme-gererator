from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,
    TemplateSendMessage, MessageTemplateAction, PostbackTemplateAction, ButtonsTemplate
)

from bs4 import BeautifulSoup as bs 
import requests
import random

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

def random_meme():
    url = 'https://memes.tw/wtf'
    header = {'User-Agent': 'Custom'}
    page_num = random.randint(1, 10)
    img_num = random.randint(0, 9)
    payload = {'page': page_num}
    img = bs(requests.get(url,headers = header, params = payload).text ,"lxml").find_all(class_='img-fluid')[img_num]['data-src']
    return img


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
    if event.message.text == "抽迷因":
        img_url = random_meme()
        reply_msg = ImageSendMessage(
            original_content_url = img_url,
            preview_image_url = img_url
            )
    elif event.message.text == "迷因頻道":
        reply_msg = TemplateSendMessage(
            alt_text='迷因主題',
            template = ButtonsTemplate(
              title='我自己做的',
              text='共有 16,159 張圖片',
              thumbnail_image_url="https://memes.tw/user-wtf/1624245841223.jpg",
              actions=[
                  PostbackTemplateAction(
                      label='選擇主題',
                      text='選擇主題',
                      data='value data'
                  ),
                  MessageTemplateAction(
                      label='換個主題',
                      text='迷因頻道'
                  )
              ]
          )
      )
    
    line_bot_api.reply_message(event.reply_token, reply_msg)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)