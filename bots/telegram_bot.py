from datetime import datetime
import telebot
import os
from models.openai_chat import gpt_35_api_stream, INTRO_MSG
from secrets import TELEGRAM_BOT_TOKEN, TELEGRAM_SPECIFIC_ACCOUNT_ID
from models.soulchat import chat_with_soulchat

BOT_TOKEN = TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)
SPECIFIC_ACCOUNT_ID = TELEGRAM_SPECIFIC_ACCOUNT_ID

user_chat_histories = {}


@bot.message_handler(commands=['start'])
def send_intro(message):
    intro = "你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！"
    bot.send_message(message.chat.id, intro)
    bot.send_message(message.chat.id,
                     "本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
    user_chat_histories[message.chat.id] = {
        'history': [
            {'role': 'system', 'content': INTRO_MSG},
            {'role': 'user', 'content': INTRO_MSG}
        ],
        'mode': 'ChatGPT'
    }
    gpt_35_api_stream(user_chat_histories[message.chat.id]['history'])


@bot.message_handler(commands=['change'])
def change_mode(message):
    mode = message.text.split()[1]
    if mode not in ['ChatGPT', 'SoulChat']:
        bot.send_message(message.chat.id, "无效的模式。请使用 /change ChatGPT 或 /change SoulChat。")
        return
    user_chat_histories[message.chat.id]['mode'] = mode
    bot.send_message(message.chat.id, f"已切换到 {mode} 模式。")


@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if message.chat.id not in user_chat_histories:
        send_intro(message)

    user_input = {
        'role': 'user',
        'content': message.text
    }
    user_chat_histories[message.chat.id]['history'].append(user_input)

    if user_chat_histories[message.chat.id]['mode'] == 'ChatGPT':
        success, error_msg = gpt_35_api_stream(user_chat_histories[message.chat.id]['history'])
        if not success:
            bot.send_message(message.chat.id, "抱歉，我遇到了一个错误。")
            return
        gpt_response = user_chat_histories[message.chat.id]['history'][-1]['content']
    else:  # mode is 'SoulChat'
        gpt_response = chat_with_soulchat(message.text)

    bot.send_message(message.chat.id, gpt_response)

    if not os.path.exists("logs"):
        os.mkdir("logs")
    account_dir = os.path.join("logs", str(message.chat.id))
    if not os.path.exists(account_dir):
        os.mkdir(account_dir)
    file_path = os.path.join(account_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"用户: {user_input['content']}\n")
        f.write(f"机器人: {gpt_response}\n")


@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_chat_histories.pop(message.chat.id, None)
    send_intro(message)


def start_bot():
    bot.infinity_polling()
