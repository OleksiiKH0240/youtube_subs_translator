import os
import sys
from googletrans import Translator
from Benchmarks_funcs.Benchmarks import benchmark
import time

from config_paths import get_paths


class FileTranslator:
    def __init__(self, subs_folder_path: str = ""):
        self.subs_folder_path = subs_folder_path
        if subs_folder_path:
            if ":" not in subs_folder_path:
                # relative path (path started from _parser folder)
                self.subs_folder_path = get_paths(["translator"])[0] + "\\" + subs_folder_path
            if not os.path.exists(subs_folder_path):
                os.mkdir(subs_folder_path)

        self.translator = Translator()
        print('Start Translator')

    @benchmark
    def trans_file(self, subs_file_name: str = 'test_file_input.txt'):
        print('Start Translate file')

        words = set()
        words_splitter = ' '
        with open(self.subs_folder_path + "\\" + subs_file_name
                  if self.subs_folder_path else subs_file_name, 'r', encoding='utf-8') as f:
            for word in [j for i in f.readlines() for j in i[:-1].split(words_splitter)]:
                for extra_symbol in ",.?'\"":
                    # print(f"extra_symbol={extra_symbol}; word={word}")
                    word = word.replace(extra_symbol, "")
                words.add(word.lower())
            words.discard('')
        words = list(words)
        print(words)
        # print(";".join(words))

        # translated_words = [self.translator.translate(i, dest='ru').text for i in words]
        words_splitter = '##\n##'
        # print(words_splitter.join(words))
        # cool crutches
        while True:
            try:
                translated_words = []

                for i in self.translator.translate(words_splitter.join(words), dest='ru').text.split(
                        words_splitter):
                    # print(i)
                    translated_words.append(i)

            except AttributeError:
                print('AttributeError in Translator')
                self.translator = Translator()
                time.sleep(0.4)
                continue
            break
        # cool crutches
        # print(";".join(translated_words))
        print(translated_words)
        new_sub_file_name = subs_file_name[0:-4] + '_translated' + subs_file_name[-4:]
        # assert len(words) == len(translated_words)
        with open(self.subs_folder_path + "\\" + new_sub_file_name
                  if self.subs_folder_path else new_sub_file_name, 'w', encoding='utf-8') as f:
            new_file_str = '\n'.join(map(lambda x, y: x + ' - ' + y, words, translated_words)) + '\n'
            f.write(new_file_str)
            return self.subs_folder_path, new_sub_file_name


if __name__ == '__main__':
    os.chdir(sys.path[0])
    print('Translator start')
    f_tr = FileTranslator()
    print(f_tr.trans_file())
