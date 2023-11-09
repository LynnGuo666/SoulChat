# 導入Discord.py模組
import discord
import os
# 導入commands指令模組
from discord.ext import commands
from discord import app_commands

from models.openai_chat import gpt_35_api_stream, INTRO_MSG

from secrets import DC_BOT_TOKEN

# intents是要求機器人的權限
intents = discord.Intents.all()
# command_prefix是前綴符號，可以自由選擇($, #, &...)
bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
# 启动说明
async def on_ready():
  print(f"目前登入身份 --> {bot.user}")

user_chat_histories = {}  #用户记录字典创建

@bot.command()
# 输入%start开始指令
async def start(ctx):
  await ctx.send("你好呀，这里是心灵加油站，如果你想要得到我的帮助的话，请你介绍下自己吧！")
  await ctx.send("本对话中的医学内容仅供参考，并不能视作专业意见。如需获取医疗帮助或意见，请咨询专业人士。详见医学声明.")
  user_chat_histories = {}
  user = ""
  button = discord.ui.Button(style=discord.ButtonStyle.primary,
                             label="点击继续（点击即视为同意隐私条例）")

  #按钮按下【正式开始】
  async def button_callback(i):
    user = i.user
    print(user)
    while True:  # 创建一个无限循环
      try:
        # 等待用户发送消息
        message = await bot.wait_for(
            'message',
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        user_chat_histories[message.id] = {
            'history': [{
                'role': 'system',
                'content': INTRO_MSG
            }, {
                "role": "user",
                "content": INTRO_MSG
            }],
            'mode':
            'ChatGPT'
        }
        #【待修BUG】 确保消息不是 bot 的命令
        # 对用户的消息作出响应
        user_input={
          'role': 'user',
          'content': message.content
        }
        user_chat_histories[message.id]['history'].append(user_input)
        gpt_35_api_stream(user_chat_histories[message.id]['history'])
        gpt_response = user_chat_histories[
            message.id]['history'][-1]['content']
        await ctx.send(gpt_response)
        
      except Exception as e:
        print(f'Error: {e}')
        break  #如果发生错误，退出循环

  button.callback = button_callback
  # Need to create a view
  buttons_view = discord.ui.View()
  # and add the button component to the view
  buttons_view.add_item(button)
  # send the view with the message
  await ctx.send("请继续：", view=buttons_view)


def start_bot():
  bot.run(DC_BOT_TOKEN)
