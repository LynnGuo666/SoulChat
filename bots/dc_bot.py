import os
import discord
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
    await ctx.send("你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！")
    await ctx.send("本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")

    user_chat_histories[ctx.author.id] = {
        'history': [{'role': 'system', 'content': INTRO_MSG},
                    {'role': 'user', 'content': INTRO_MSG}],
        'mode': 'ChatGPT'
    }

    user = ctx.author
    button = Button(style=discord.ButtonStyle.primary, label="点击继续（点击即视为同意隐私条例）")

    async def button_callback(i, user=user):
        try:
            # 发送等待消息的卡片
            wait_message = await ctx.send("正在处理，请稍候...")

            message = await bot.wait_for('message', check=lambda m: m.author == user and m.channel == ctx.channel, timeout=60)
            user_input = {'role': 'user', 'content': message.content}
            user_chat_histories[user.id]['history'].append(user_input)
            gpt_35_api_stream(user_chat_histories[user.id]['history'])
            gpt_response = user_chat_histories[user.id]['history'][-1]['content']

            # 修改等待消息卡片为ChatGPT的回复
            await wait_message.edit(content=gpt_response)
        except discord.DiscordException as e:
            print(f'Discord error: {e}')
            await ctx.send("发生了错误，请稍后再试。")
        except asyncio.TimeoutError:
            await ctx.send("操作超时，请重新开始.")

        button.disabled = True  # 禁用按钮

    button.callback = button_callback
    buttons_view = View()
    buttons_view.add_item(button)
    await ctx.send("请继续：", view=buttons_view)

def start_bot():
    bot.run(DC_BOT_TOKEN)
