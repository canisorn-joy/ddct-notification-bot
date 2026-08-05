import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = "zJHZpF/yAMkU3IiKHYrDqnfimAA08ZqZwQLrZaoYb3DLY6Ib9Ew4W8QJv5fQo15NOtQq2PGwDIwk//eHQycD24zR+XUcCK1GP6oaUo/i22X0KGukIxEdVOcn8id3KIwcr0EjeNCrvIjhNjhNclAoWQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14bad5ee7aeaea580aa461a878fc364a"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 1. Group ID ของกลุ่มสตาฟ
STAFF_GROUP_ID = "Cd77115351ec001e12873a5df8fc30ed6"

# 2. Openchat ID ของนักศึกษาแต่ละชั้นปี (นำ ID ที่ขึ้นต้นด้วย C มาใส่ในช่องว่างเมื่อพร้อมใช้งาน)
OPENCHAT_GROUPS = {
    "DDCT 2569": "",
    "DDCT 2568": "",
    "DDCT 2567": "",
    "DDCT 2566": "",
    "DDCT 2565": "",
}

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
    
    # ถ้าพิมพ์มาทางแชทส่วนตัว (User) หาบอท
    if event.source.type == 'user':
        try:
            # ดึงวันที่ปัจจุบันในรูปแบบภาษาอังกฤษ (เช่น 05 August 2026)
            now = datetime.now()
            current_date_str = now.strftime("%d %B %Y")
            
            # จัดรูปแบบข้อความประกาศ
            announcement_text = f"Announcement ({current_date_str}) \n\n{user_message}"
            
            success_targets = []
            
            # 1. ส่งเข้ากลุ่มสตาฟ
            if STAFF_GROUP_ID:
                line_bot_api.push_message(STAFF_GROUP_ID, TextSendMessage(text=announcement_text))
                success_targets.append("กลุ่มสตาฟ")
            
            # 2. วนลูปส่งเข้า Openchat ชั้นปีต่างๆ (ถ้าใส่ ID ไว้ บอทจะส่งให้เอง)
            for batch_name, group_id in OPENCHAT_GROUPS.items():
                if group_id and not group_id.startswith("ใส่_"):
                    try:
                        line_bot_api.push_message(group_id, TextSendMessage(text=announcement_text))
                        success_targets.append(batch_name)
                    except Exception as e:
                        print(f"Error sending to {batch_name}: {str(e)}")
            
            # ตอบกลับคนส่งในแชทส่วนตัว
            report = f"✅ ส่งประกาศสำเร็จไปยัง: {', '.join(success_targets)}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=report))
            
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"❌ เกิดข้อผิดพลาด: {str(e)}"))
