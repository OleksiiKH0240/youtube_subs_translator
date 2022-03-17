import logging
from os.path import join

from aiogram import Bot, Dispatcher, executor

from _bot import config
import os
import sys


from _bot.config import get_paths, get_base_path

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
# print('fgdf', sys.path)
# print(os.getcwd())

os.chdir(sys.path[0])

data_folder_path = get_paths(["data"])[0]
# print(data_folder_path)
if not os.path.exists(data_folder_path):
    base_path = get_base_path()
    os.mkdir(join(base_path, "_data"))


for folder_name in [config.Buffer_folder_name, config.Parser_folder_name]:
    if not os.path.exists(join(data_folder_path, folder_name)):
        os.mkdir(join(data_folder_path, folder_name))

if __name__ == "__main__":
    #print(os.getcwd())
    #os.chdir(sys.path[0])
    from _bot.you_su_aiorgam_bot_handlers import dp, say_to_admin
    executor.start_polling(dp, on_startup=say_to_admin)
