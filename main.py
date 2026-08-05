import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

# Token และ Secret ของคุณ
LINE_CHANNEL_ACCESS_TOKEN = "zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14bad5ee7aeaea580aa461a878fc364a"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ➡️ 1. ใส่ User ID ส่วนตัวของคุณ (คนที่มีสิทธิ์ส่งประกาศ)
YOUR_USER_ID = "U1a8d3824015f449b8c5ea2a56cf33b76"

# ➡️ 2. ใส่ Group ID ของกลุ่มสตาฟที่ได้มาจากขั้นตอนด้านบน
STAFF_GROUP_ID = "Cd77115351ec001e12873a5df8fc30ed6"

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # เงื่อนไข: ต้องเป็นคุณส่งมาจากแชทส่วนตัว (Private Chat) เท่านั้น
    if event.source.type == 'user' and event.source.user_id == YOUR_USER_ID:
        if user_message.startswith("Cancel") or user_message.startswith("Announcement"):
            formatted_message = (  f"{user_message}\n\n"   )
            
            try:
                # ส่งข้อความตรงเข้ากลุ่มสตาฟ
                line_bot_api.push_message(STAFF_GROUP_ID, TextSendMessage(text=formatted_message))
                
                # รายงานผลกลับมาหาคุณในแชทส่วนตัว
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ ส่งประกาศเข้ากลุ่มสตาฟสำเร็จ!"))
            except Exception as e:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ เกิดข้อผิดพลาด: {str(e)}"))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="วิธีใช้งาน: พิมพ์ขึ้นต้นด้วย 'Cancel' หรือ 'Announcement' ตามด้วยเนื้อหาที่ต้องการประกาศครับ")
            )
    else:
        # ถ้าไม่ใช่คุณ หรือมีคนพิมพ์ในกลุ่ม บอทจะไม่ตอบโต้อะไร
        pass
