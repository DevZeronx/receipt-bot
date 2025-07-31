import telebot
import requests
import os
from io import BytesIO

API_URL = os.getenv("API_URL")  # https://your-project.vercel.app/api/receipt
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@bot.message_handler(commands=["start"])
def start(msg):
    chat = msg.chat.id
    bot.send_message(chat, "স্বাগতম! কতটি পণ্য রসিদে থাকবে?")
    user_data[chat] = {"step": "ask_count"}

@bot.message_handler(func=lambda m: m.chat.id in user_data)
def handle(m):
    chat = m.chat.id
    state = user_data[chat]

    if state["step"] == "ask_count":
        try:
            cnt = int(m.text)
            state.update({"count": cnt, "products": [], "idx": 0})
            bot.send_message(chat, f"পণ্যের নাম লিখুন #1")
            state["step"] = "ask_name"
        except:
            bot.send_message(chat, "যথাযথ সংখ্যা দিন, যেমন: ৩")
    elif state["step"] == "ask_name":
        state["products"].append({"name": m.text})
        bot.send_message(chat, f"💰 দাম লিখুন #{state['idx']+1}")
        state["step"] = "ask_price"
    elif state["step"] == "ask_price":
        try:
            price = float(m.text)
            state["products"][state["idx"]]["price"] = price
            state["idx"] += 1
            if state["idx"] < state["count"]:
                bot.send_message(chat, f"নাম লিখুন #{state['idx']+1}")
                state["step"] = "ask_name"
            else:
                bot.send_message(chat, "🎟️ রসিদ তৈরি হচ্ছে…")
                resp = requests.post(API_URL, json={"products": state["products"]})
                if resp.status_code == 200:
                    pdf = BytesIO(resp.content)
                    bot.send_document(chat, pdf, visible_file_name="receipt.pdf", caption="✅ এটা আপনার রসিদ।")
                else:
                    bot.send_message(chat, f"Error: {resp.text}")
                del user_data[chat]
        except:
            bot.send_message(chat, "মূল্য সঠিকভাবে লিখুন, যেমন: ৯৯.৫০")

bot.polling()
