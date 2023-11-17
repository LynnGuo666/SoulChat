from bots import telegram_bot

from bots import line_bot
import os
from bots.line_bot import app

from bots import dc_bot

# from keep_alive import keep_alive

if __name__ == '__main__':
  # telegram_bot.start_bot()
  # keep_alive()
  # linebot
  # port = int(os.environ.get('PORT', 5000))
  # app.run(host='0.0.0.0', port=port)
  dc_bot.start_bot()


