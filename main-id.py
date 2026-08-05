import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

app = FastAPI()
line_bot_api = LineBotApi("zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("14bad5ee7aeaea580aa461a878fc364a")

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    handler.handle(body.decode("utf-8"), signature)
    return "OK"

@handler.add(MessageEvent, message=TextSendMessage)
def handle_message(event):
    if event.source.type == 'user':
        reply_text = f"Your User ID is:\n{event.source.user_id}"
    elif event.source.type == 'group':
        reply_text = f"This Group ID is:\n{event.source.group_id}"
    else:
        reply_text = "Unknown"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))