import os
import openai
import telebot
from datetime import datetime
os.environ['PYTHONIOENCODING'] = 'UTF-8'
# OpenAI 配置
openai.api_key = "" #OpenAI API
openai.api_base = "" #OpenAI API Url
SPECIFIC_ACCOUNT_ID = 0 # Telegram通知用户ID
# Telegram 配置
BOT_TOKEN = "" # Telegram BOT Token
bot = telebot.TeleBot(BOT_TOKEN)

# 为每个用户初始化聊天历史
user_chat_histories = {}

# 欢迎消息
INTRO_MSG = "我希望你扮演一名专业的心理医生，你可以跟我聊天并给我合理的建议与方式，有必要时你可以安慰我。你需要以温柔、体贴、亲切的语气。你的聊天风格特别可爱有趣，你的每一个回答都要体现这一点。你可以加一些emoji。同时，如果你认为我的对话存在自杀风险，请你在对话中直接回答【需要介入】，不要返回其他语句，这样会有一位专业的心理医生和医疗团队来帮助我。同时，一定要记住：请在你每次回答的末尾都加上风险评估的参数，如（风险评估：高）。"
# GPT-3.5 API 流式处理函数
def gpt_35_api_stream(messages: list):
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.6,
            stream=True,
        )
        completion = {'role': '', 'content': ''}
        for event in response:
            if event['choices'][0]['finish_reason'] == 'stop':
                break
            for delta_k, delta_v in event['choices'][0]['delta'].items():
                completion[delta_k] += delta_v
        messages.append(completion)
        return (True, '')
    except Exception as err:
        return (False, f'OpenAI API 异常: {err}')

# 处理 /start 命令的函数
@bot.message_handler(commands=['start'])
def send_intro(message):
    intro = "你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！"
    bot.send_message(message.chat.id, intro)
    bot.send_message(message.chat.id, "本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
    user_chat_histories[message.chat.id] = [
        {'role': 'system', 'content': INTRO_MSG},
        {'role': 'user', 'content': INTRO_MSG}
    ]
    gpt_35_api_stream(user_chat_histories[message.chat.id])  # 初始化AI的角色

# 处理其他消息的函数
@bot.message_handler(func=lambda msg: True)
def chat_with_gpt(message):
    if message.chat.id not in user_chat_histories:
        send_intro(message)

    user_input = {
        'role': 'user',
        'content': message.text
    }
    user_chat_histories[message.chat.id].append(user_input)
    print(f"用户消息: {message.chat.id},{user_input['content']}")

    # 使用OpenAI获取ChatGPT的回复
    success, error_msg = gpt_35_api_stream(user_chat_histories[message.chat.id])
    if not success:
        bot.send_message(message.chat.id, "抱歉，我遇到了一个错误。")
        return

    gpt_response = user_chat_histories[message.chat.id][-1]['content']

    # 风险评估参数（您可以进一步优化此参数）

    if "需要介入" in gpt_response:
        # 发送报告并通知特定账户
        bot.send_message(message.chat.id, gpt_response)
        bot.send_message(SPECIFIC_ACCOUNT_ID, f"【风险警告】侦测到用户{message.chat.id}需要介入处理。{user_chat_histories}")  # 添加报告内容
        return
    if "风险评估：高" in gpt_response:
        # 发送报告并通知特定账户
        bot.send_message(message.chat.id, gpt_response)
        bot.send_message(SPECIFIC_ACCOUNT_ID, f"【风险警告】侦测到用户{message.chat.id}需要介入处理。{user_chat_histories}")  # 添加报告内容
        return    

    # 将用户消息和ChatGPT的回复打印到终端
    print(f"用户消息: {user_input['content']}")
    print(f"ChatGPT的回复: {gpt_response}")

    # 将ChatGPT的回复发送给用户
    bot.send_message(message.chat.id, gpt_response)

    # 保存对话到本地文件
    with open(f"{message.chat.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "a") as f:
        f.write(f"用户: {user_input['content']}\n")
        f.write(f"机器人: {gpt_response}\n")

# 处理 /reset 命令的函数
@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_chat_histories.pop(message.chat.id, None)
    send_intro(message)

if __name__ == '__main__':
    bot.infinity_polling()
