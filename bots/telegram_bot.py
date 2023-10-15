from datetime import datetime

import telebot
import os
from models.openai_chat import gpt_35_api_stream, INTRO_MSG
from secrets import TELEGRAM_BOT_TOKEN, TELEGRAM_SPECIFIC_ACCOUNT_ID

BOT_TOKEN = TELEGRAM_BOT_TOKEN  # Telegram BOT Token

bot = telebot.TeleBot(BOT_TOKEN)
SPECIFIC_ACCOUNT_ID = TELEGRAM_SPECIFIC_ACCOUNT_ID  # Telegram通知用户ID

user_chat_histories = {}


@bot.message_handler(commands=['start'])
def send_intro(message):
    intro = "你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！"
    bot.send_message(message.chat.id, intro)
    bot.send_message(message.chat.id,
                     "本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
    user_chat_histories[message.chat.id] = [
        {'role': 'system', 'content': INTRO_MSG},
        {'role': 'user', 'content': INTRO_MSG}
    ]
    gpt_35_api_stream(user_chat_histories[message.chat.id])  # 初始化AI的角色


@bot.message_handler(func=lambda msg: True)
def chat_with_gpt(message):
    if message.chat.id not in user_chat_histories:
        send_intro(message)

    user_input = {
        'role': 'user',
        'content': message.text
    }
    user_chat_histories[message.chat.id].append(user_input)

    # 使用OpenAI获取ChatGPT的回复
    success, error_msg = gpt_35_api_stream(user_chat_histories[message.chat.id])
    if not success:
        bot.send_message(message.chat.id, "抱歉，我遇到了一个错误。")
        return

    gpt_response = user_chat_histories[message.chat.id][-1]['content']

    if "需要介入" in gpt_response:
        # 发送报告并通知特定账户
        bot.send_message(message.chat.id, gpt_response)
        bot.send_message(SPECIFIC_ACCOUNT_ID,
                         f"【风险警告】侦测到用户{message.chat.id}需要介入处理。{user_chat_histories}")  # 添加报告内容
        return
    if "风险评估：高" in gpt_response:
        # 发送报告并通知特定账户
        bot.send_message(message.chat.id, gpt_response)
        bot.send_message(SPECIFIC_ACCOUNT_ID,
                         f"【风险警告】侦测到用户{message.chat.id}需要介入处理。{user_chat_histories}")  # 添加报告内容
        return

        # 将用户消息和ChatGPT的回复打印到终端
    print(f"用户消息: {user_input['content']}")
    print(f"ChatGPT的回复: {gpt_response}")

    # 将ChatGPT的回复发送给用户
    bot.send_message(message.chat.id, gpt_response)

    # 确保logs目录存在
    if not os.path.exists("logs"):
        os.mkdir("logs")

    # 为每个账号创建子目录
    account_dir = os.path.join("logs", str(message.chat.id))
    if not os.path.exists(account_dir):
        os.mkdir(account_dir)

    # 定义文件保存路径
    file_path = os.path.join(account_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")

    # 保存聊天记录
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"用户: {user_input['content']}\n")
        f.write(f"机器人: {gpt_response}\n")


@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_chat_histories.pop(message.chat.id, None)
    send_intro(message)


def start_bot():
    bot.infinity_polling()
