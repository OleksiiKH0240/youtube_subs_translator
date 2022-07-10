import asyncio
import multiprocessing
import os
from multiprocessing import Pool
from multiprocessing.managers import ValueProxy
from os.path import join
import sys
from typing import Union, List, Dict, Optional

import httpcore
from httpcore import SyncHTTPProxy
from googletrans import Translator
from googletrans.models import Translated

from Benchmarks_funcs.Benchmarks import benchmark
from _parser.textParser import TextParser
import time

from _bot.config import get_paths, get_base_path


class FileTranslator:
    @benchmark()
    def __init__(self, subs_folder_path: str = ""):
        self.subs_folder_path = subs_folder_path
        if subs_folder_path:
            if ":" not in subs_folder_path:
                # relative path (path started from _parser folder)
                self.subs_folder_path = join(get_paths(["translator"])[0], subs_folder_path)
            if not os.path.exists(subs_folder_path):
                os.mkdir(subs_folder_path)

        self.textTranslator = TextTranslator()
        print('Start File Translator')

    @benchmark()
    def trans_file(self, subs_file_name: str = 'test_file_input.txt'):
        print('Start Translate file')

        with open(join(self.subs_folder_path, subs_file_name) if self.subs_folder_path != "" else subs_file_name,
                  'r', encoding='utf-8') as f:
            text = f.read()

        wordsDict = self.textTranslator.transText(text)
        words = wordsDict["words"]
        translatedWords = wordsDict["translatedWords"]

        # print(translatedWords)
        new_sub_file_name = subs_file_name[0:-4] + '_translated' + subs_file_name[-4:]

        # print('\n'.join(map(lambda x, y: x + ' - ' + y, words, translatedWords)))

        assert len(words) == len(translatedWords)

        with open(join(self.subs_folder_path, new_sub_file_name)
                  if self.subs_folder_path != "" else new_sub_file_name, 'w', encoding='utf-8') as f:
            new_file_str = '\n'.join(map(lambda x, y: x + ' - ' + y, words, translatedWords)) + '\n'
            f.write(new_file_str)

        return self.subs_folder_path, new_sub_file_name


class TextTranslator:
    textParser = TextParser()

    proxyFilePath = r"resources\proxy_scraper_checker\proxies\http.txt"

    os.chdir(get_base_path())

    # if not os.path.exists(proxyFilePath):
    #     from resources.proxy_scraper_checker.main import main as proxy_main
    #     asyncio.run(proxy_main())

    # with open(proxyFilePath, "r") as f:
    #     proxiesList = ["localhost"] + [i[:-1] for i in f.readlines()]

    os.chdir(get_paths(["translator", ])[0])

    errors2changeIp = 10
    iterations2changeIp = 100
    proxyIdx: Union[int, ValueProxy] = 0
    errorsCount: Union[int, ValueProxy] = 0
    iterationsCount: Union[int, ValueProxy] = 0

    def __init__(self, errors2changeIp=None, iterations2changeIp=None):
        # if errors2changeIp is None:
        #     TextTranslator.errors2changeIp = errors2changeIp
        # if iterations2changeIp is None:
        #     TextTranslator.iterations2changeIp = iterations2changeIp

        print("Start Text Translator")

    def incrErrorsCountByN(self, N: int) -> None:
        if type(TextTranslator.errorsCount) is int:
            TextTranslator.errorsCount += N
        else:
            TextTranslator.errorsCount.value += N

    def incrIterationsCountByN(self, N: int) -> None:
        if type(TextTranslator.iterationsCount) is int:
            TextTranslator.iterationsCount += N
        else:
            TextTranslator.iterationsCount.value += N

    # def increaseProxyIdxByN(self, N: int) -> None:
    #     if type(TextTranslator.proxyIdx) is int:
    #         TextTranslator.proxyIdx += N
    #         TextTranslator.proxyIdx = TextTranslator.proxyIdx % len(TextTranslator.proxiesList)
    #     else:
    #         TextTranslator.proxyIdx.value += N
    #         TextTranslator.proxyIdx.value = TextTranslator.proxyIdx.value % len(TextTranslator.proxiesList)
    #
    # def getProxyDictByProxyIdx(self, proxyIdx: Union[int, ValueProxy]):
    #     idx = proxyIdx if type(proxyIdx) is int else proxyIdx.value
    #     if "localhost" == self.proxiesList[idx]:
    #         return {}
    #     else:
    #         ip, port = self.proxiesList[idx].split(":")
    #         return {"https": SyncHTTPProxy((b'http', f'{ip}'.encode(), int(port), b''))}
    #
    def getElementValue(self, element: Union[int, ValueProxy]):
        return element if type(element) is int else element.value

    @benchmark()
    def transText(self, text: str) -> Dict[str, List]:
        """
        return: {"words": [ .... ], "translatedWords": [ ... ]}
        """
        words = []
        translatedWords = []
        wordsDict = self.textParser.parse(text)

        for pos, wordsSet in wordsDict.items():
            if len(wordsSet) != 0:
                wordsSet = list(wordsSet)
                words.extend(wordsSet)
                # todo: change all back
                if pos in ["prepositional_verb", "phrasal_verb"]:
                    wordsSet = [self.textParser.phrasalVerbsDict[phrasalV].split("\n")[0] for phrasalV in wordsSet]

                if len(wordsSet) > int(6 * 0.75 * os.cpu_count()):
                    # wordsMod = self.transWords(wordsSet, pos=pos)
                    wordsMod = self.transWordsWithNCores(wordsList=wordsSet, pos=pos)
                else:
                    wordsMod = self.transWords(wordsList=wordsSet, pos=pos)

                if pos != "proper_noun":
                    wordsMod = map(lambda x: x.lower(), wordsMod)
                # wordsMod = list(filter(lambda x: x not in translatedWords, wordsMod))

                translatedWords.extend(wordsMod)

        return {"words": words, "translatedWords": translatedWords}

    @benchmark(kwargs2show=["pos", ])
    def transWords(self, wordsList: List = [], pos: str = "",
                   iters: Optional[ValueProxy] = None,
                   errors: Optional[ValueProxy] = None,
                   proxyIdx: Optional[ValueProxy] = None) -> Union[List[str,], int]:


        words_splitter = "\n\n\n"
        time2sleep = 0.2
        translated_words = []
        # print(f"{TextTranslator.iterationsCount=}")
        if len(wordsList) == 0:
            print("TextTranslator: transWords: wordsList variable has no elements")
            return -1

        if iters is not None and errors is not None and proxyIdx is not None:
            # case when this function is invoked in multiprocessing
            # and iters, errors, proxyIdx are shared memory objects
            TextTranslator.iterationsCount = iters
            TextTranslator.errorsCount = errors
            TextTranslator.proxyIdx = proxyIdx

        # currProxy = self.getProxyDictByProxyIdx(TextTranslator.proxyIdx)
        # translator = Translator(proxies=currProxy)
        translator = Translator()

        # cool crutches
        while True:
            if self.getElementValue(TextTranslator.errorsCount) >= TextTranslator.errors2changeIp:

                # self.increaseProxyIdxByN(1)
                # currProxy = self.getProxyDictByProxyIdx(TextTranslator.proxyIdx)
                # translator.client.proxies = currProxy

                # set iterations and errors to zero
                self.incrErrorsCountByN(-self.getElementValue(TextTranslator.errorsCount))
                self.incrIterationsCountByN(-self.getElementValue(TextTranslator.iterationsCount))

            try:
                if pos == "":
                    for i in translator.translate(words_splitter.join(wordsList), src="en", dest='ru').text.split(
                            words_splitter):
                        # print(i)
                        translated_words.append(i)
                    self.incrIterationsCountByN(1)
                else:
                    for word in wordsList:
                        if self.getElementValue(TextTranslator.iterationsCount) >= TextTranslator.iterations2changeIp:
                            self.increaseProxyIdxByN(1)

                            # set iterations and errors to zero
                            self.incrErrorsCountByN(-self.getElementValue(TextTranslator.errorsCount))
                            self.incrIterationsCountByN(-self.getElementValue(TextTranslator.iterationsCount))

                        # currProxy = self.getProxyDictByProxyIdx(TextTranslator.proxyIdx)
                        # translator.client.proxies = currProxy

                        # t0=time.time()
                        translated_obj: Translated = translator.translate(word, src="en", dest="ru")
                        self.incrIterationsCountByN(1)
                        # print("time elapsed:", time.time() - t0)
                        translated_word: Union[str, int] = self.getWordTranslateByPos(
                            translatedObj=translated_obj, pos=pos)
                        if type(translated_word) is int:
                            translated_word = translated_obj.text

                        translated_words.append(translated_word)

            except (AttributeError, httpcore._exceptions.ConnectTimeout, httpcore._exceptions.ReadError) as e:
                self.incrErrorsCountByN(1)
                print(f"{e} in Translator")

                translated_words = []
                time.sleep(time2sleep)
                continue
            break
        # cool crutches
        return translated_words

    @benchmark(kwargs2show=["pos", ])
    def transWordsWithNCores(self, wordsList: List = [], pos: str = "", N: int = -1) -> Union[List[str,], int]:
        if N == -1:
            if os.cpu_count() > 2:
                coresCount = int(os.cpu_count() * 0.75)
            else:
                coresCount = os.cpu_count()
        else:
            coresCount = N
        wordsNumber = len(wordsList)

        step = wordsNumber // coresCount
        if step == 0:
            wLists = [wordsList, ]
            coresCount = 1
        else:
            wLists: List[List] = [wordsList[i * step: ((i + 1) * step)] for i in range(coresCount)]
            wLists[-1].extend(wordsList[step * coresCount:])

        # print(wLists)
        translated_words = []

        with Pool(coresCount) as executor, multiprocessing.Manager() as m:
            iters = m.Value("i", TextTranslator.iterationsCount)
            errors = m.Value("i", TextTranslator.errorsCount)
            # proxyIdx = m.Value("i", TextTranslator.proxyIdx)

            # args = zip(wLists, [pos, ] * len(wLists),
            #            [iters, ] * len(wLists), [errors, ] * len(wLists), [proxyIdx, ] * len(wLists))
            args = zip(wLists, [pos, ] * len(wLists),
                       [iters, ] * len(wLists), [errors, ] * len(wLists), )

            results = executor.starmap(self.transWords, args)

            TextTranslator.iterationsCount = iters.value
            TextTranslator.errorsCount = errors.value
            # TextTranslator.proxyIdx = proxyIdx.value

        for res in results:
            translated_words.extend(res)

        return translated_words

    def f(self, *args):
        print(args, self)
        return args

    def getWordTranslateByPos(self, translatedObj: Translated, pos: str) -> Union[str, int]:
        """
        pos:  Part Of Speech from list
        ["noun", "pronoun", "adjective", "verb", "auxiliary", "adverb", "preposition", "proper_noun",
        "prepositional_verb", "phrasal_verb", ]
        """
        extra_data = translatedObj.extra_data["parsed"]
        try:
            required_data = extra_data[3][5][0]
        except IndexError:
            return -2
        except TypeError:
            return -3

        for block in required_data:
            if block[0] == pos:
                return block[1][0][0]
        else:
            return -1


if __name__ == '__main__':
    # os.chdir(sys.path[0])
    # f_tr = FileTranslator()
    # f_tr.trans_file()
    t = TextTranslator()
    # text = """encouraging this I'm not encouraging I'm. Most of my make-up wore off before I got to the party."""
    with open("../resources/friendsS01Ep03.txt", "r") as f:
        text = f.read()
    t.transText(text)
# print(t.transWordsWithNCores([1,2,3,4,5,56,6,7,8, 9, 10, 12, 34, 56], "noun"))
