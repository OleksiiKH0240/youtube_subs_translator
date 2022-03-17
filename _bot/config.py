import os
import sys
from os.path import join
from typing import List

TOKEN = os.getenv("youtube_subs_translator_token")
ADMIN_ID = os.getenv("telegram_user_id")

Parser_folder_name = 'parser_temp_files'
Buffer_folder_name = 'telegram_temp_files'

Modules_paths = ["_bot", "_parser", "_translator", "Benchmarks_funcs", "_data"]

main_folder_name = 'youtube_subs_translator'


def get_base_path() -> str:
    global main_folder_name
    base_path = os.getcwd()
    base_path = base_path[0:base_path.index(main_folder_name) + len(main_folder_name)]
    if base_path not in sys.path:
        sys.path.append(base_path)

    return base_path


Base_path = get_base_path()


# print(Base_path)

# print('Base_path: ', Base_path)
def get_paths(modules_names=None) -> List[str]:
    if modules_names is None:
        modules_names = Modules_paths

    requirement_paths = [join(Base_path, i) for i in Modules_paths if
                         any([True if j in i else False for j in modules_names])]
    for i in requirement_paths:
        if i not in sys.path:
            sys.path.append(i)

    return requirement_paths

