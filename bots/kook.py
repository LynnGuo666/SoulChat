from datetime import datetime
import os
from khl import Bot, Message
from models.openai_chat import gpt_35_api_stream, INTRO_MSG
from secrets import KOOK_Token
import asyncio

# 初始化机器人
bot = Bot(token=KOOK_Token)

# 保存用户聊天记录的字典
user_chat_histories = {}


# 注册命令，发送 `/start` 在频道中调用
@bot.command(name='start')
async def send_intro(msg: Message):
    intro = "你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！"
    await msg.reply(intro)
    await msg.reply("本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
    user_chat_histories[msg.author.id] = {
        'history': [
            {'role': 'system', 'content': INTRO_MSG},
            {'role': 'user', 'content': INTRO_MSG}
        ],
        'mode': 'ChatGPT'
    }
    gpt_35_api_stream(user_chat_histories[msg.author.id]['history'])


# 注册命令，发送 `/change 模式` 在频道中调用
@bot.command(name='change')
async def change_mode(msg: Message):
    mode = msg.content.split()[1]
    if mode not in ['ChatGPT', 'SoulChat']:
        await msg.reply("无效的模式。请使用 /change ChatGPT 或 /change SoulChat。")
        return
    user_chat_histories[msg.author.id]['mode'] = mode
    await msg.reply(f"已切换到 {mode} 模式。")


# 注册消息处理器，处理所有消息
@bot.command(regex=r'^[^/].*')
async def process_message(msg: Message):
    print(msg.content)
    if msg.author.id not in user_chat_histories:
        #         intro = "你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！"
        #         await msg.reply(intro)
        #         await msg.reply(
        #             "本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
        user_chat_histories[msg.author.id] = {
            'history': [
                {'role': 'system', 'content': INTRO_MSG},
                {'role': 'user',
                 'content': f"我的名字是{msg.author.username}，接下来我将向你咨询一些问题，如果我的对话中存在任何非心理方面的问题，你可以拒绝回答我。"}
            ],
            'mode': 'ChatGPT'
        }
        gpt_35_api_stream(user_chat_histories[msg.author.id]['history'])

    user_input = {
        'role': 'user',
        'content': msg.content
    }
    user_chat_histories[msg.author.id]['history'].append(user_input)

    if user_chat_histories[msg.author.id]['mode'] == 'ChatGPT':
        success, error_msg = gpt_35_api_stream(user_chat_histories[msg.author.id]['history'])
        if not success:
            await msg.reply("抱歉，我遇到了一个错误。")
            return
        gpt_response = user_chat_histories[msg.author.id]['history'][-1]['content']

        # 添加检测“需要介入”的条件
        if "需要介入" in gpt_response:
            ch = await bot.client.fetch_public_channel("1596011429179695")
            response_text = f"用户 {msg.author.username} 需要介入，完整对话如下：\n\n"
            response_text += "\n".join(
                [f"{item['role']}: {item['content']}" for item in user_chat_histories[msg.author.id]['history']])
            await bot.client.send(ch, response_text)

    # 使用 await 调用异步函数
    await msg.reply(gpt_response)

    if not os.path.exists("logs"):
        os.mkdir("logs")
    account_dir = os.path.join("logs", str(msg.author.id))
    if not os.path.exists(account_dir):
        os.mkdir(account_dir)
    file_path = os.path.join(account_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"用户: {user_input['content']}\n")
        f.write(f"机器人: {gpt_response}\n")


# 注册命令，发送 `/reset` 在频道中调用
@bot.command(name='reset')
async def reset_conversation(msg: Message):
    user_chat_histories.pop(msg.author.id, None)
    await send_intro(msg)


# 启动机器人
def start_bot():
    asyncio.gather(bot.run())
