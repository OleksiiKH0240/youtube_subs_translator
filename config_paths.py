import os
from os.path import join
import sys

Modules_paths = ['_bot', '_parser', '_translator', 'Benchmarks_funcs', "_data"]

main_folder_name = 'youtube_subs_translator'


def get_base_path():
    global main_folder_name
    base_path = os.getcwd()
    base_path = base_path[0:base_path.index(main_folder_name) + len(main_folder_name)]
    return base_path


Base_path = get_base_path()
# print(Base_path)

# print('Base_path: ', Base_path)
def get_paths(modules_names: list = Modules_paths):
    requirement_paths = [join(Base_path, i) for i in Modules_paths if
                         any([True if j in i else False for j in modules_names])]
    for i in requirement_paths:
        if i not in sys.path:
            sys.path.append(i)

    return requirement_paths
