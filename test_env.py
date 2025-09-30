import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print(f"Bot Token: {bot_token}")
print(f"Chat ID: {chat_id}")

if not bot_token:
    print("❌ TELEGRAM_BOT_TOKEN not set")
    exit(1)

# Test bot connection
url = f"https://api.telegram.org/bot{bot_token}/getMe"
response = requests.get(url)

if response.status_code == 200:
    bot_info = response.json()
    if bot_info['ok']:
        print(f"✅ Bot is working: @{bot_info['result']['username']}")
        
        # Test sending a message
        if chat_id:
            message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': 'Test message from Python script',
                'parse_mode': 'HTML'
            }
            msg_response = requests.post(message_url, json=payload)
            if msg_response.status_code == 200:
                print("✅ Test message sent successfully!")
            else:
                print(f"❌ Failed to send message: {msg_response.text}")
        else:
            print("⚠️  TELEGRAM_CHAT_ID not set")
    else:
        print("❌ Bot connection failed")
else:
    print(f"❌ Error connecting to bot: {response.status_code} - {response.text}")