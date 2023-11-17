import os
import discord
import asyncio
import logging
from discord.ext import commands
from discord.ui import Button, View

from models.openai_chat import gpt_35_api_stream, INTRO_MSG

from secrets import DC_BOT_TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents)

user_chat_histories = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.command()
async def start(ctx):
    # 检查用户是否已同意隐私协议
    if ctx.author.id not in user_chat_histories:
        await ctx.send("你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！")
        await ctx.send("本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")

        user_chat_histories[ctx.author.id] = {
            'history': [{'role': 'system', 'content': INTRO_MSG},
                        {'role': 'user', 'content': INTRO_MSG}],
            'mode': 'ChatGPT',
            'agreed_to_privacy': False  # 添加一个标志
        }

        user = ctx.author
        button = Button(style=discord.ButtonStyle.primary, label="点击继续（点击即视为同意隐私条例）")

        async def button_callback(i, user=user):
            try:
                print("收到确认指令")
                user_chat_histories[user.id]['agreed_to_privacy'] = True  # 用户同意隐私协议
                await ctx.send("嗨嗨！你好呀！我是你的心理医生小助手，来陪你聊天和倾听你的心声。有什么让你感到烦恼或者困扰的事情吗？来和我分享一下吧！😊")
                while True:
                    try:
                        # 等待用户输入，设置超时为120秒
                        message = await bot.wait_for('message',
                                                     check=lambda m: m.author == user and m.channel == ctx.channel,
                                                     timeout=120)
                    except asyncio.TimeoutError:
                        await ctx.send("对话已超时。如果需要继续，请重新发送 `%start` 命令。")
                        break

                    user_input = {'role': 'user', 'content': message.content}
                    user_chat_histories[user.id]['history'].append(user_input)

                    try:
                        # 发送 ChatGPT 的回复
                        gpt_35_api_stream(user_chat_histories[user.id]['history'])
                        gpt_response = user_chat_histories[user.id]['history'][-1]['content']
                        await ctx.send(gpt_response)

                        # Log the conversation
                        log_message = f"User: {user_input['content']}\nBot: {gpt_response}\n"
                        print(log_message)  # 打印到终端
                        logging.info(log_message)
                    except Exception as gpt_error:
                        print(f'Error in ChatGPT response: {gpt_error}')
                        await ctx.send("抱歉，我遇到了一个错误。请稍后再试.")
                        break

            except discord.DiscordException as e:
                print(f'Discord error: {e}')
                await ctx.send("发生了错误，请稍后再试.")

    button.callback = button_callback
    buttons_view = View()
    buttons_view.add_item(button)
    await ctx.send("请继续：", view=buttons_view)

def start_bot():
    bot.run(DC_BOT_TOKEN)

if __name__ == "__main__":
    start_bot()
