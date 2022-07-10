import re

from typing import Dict, List, Set, Tuple, Union

import spacy

import nltk
# nltk.download('wordnet')
# nltk.download('omw-1.4')

from autocorrect import Speller

from Benchmarks_funcs.Benchmarks import benchmark
import _bot.config


def getPhrasalVerbsDictFromTxtFile(filePath: str = r"..\resources\phrasalVerbs.txt") -> Dict:
    with open(filePath, "r") as f:
        inStr = f.read()
    blocks = inStr.split("\n\n")

    try:
        blocks.remove("")
    except ValueError:
        pass

    phrasalVerbsDict = dict()
    # s = set()
    for block in blocks:
        block: str
        idx = block.index("\n")
        phrasalVerbsDict[block[: idx]] = block[idx + 1:]
        # patt = tuple([i if "some" in i else "word" for i in block[: idx].split(" ")])
        # s.add(patt)
    # print(s)
    return phrasalVerbsDict


class TextParser:
    nlp = spacy.load("en_core_web_sm")
    speller = Speller(lang='en')

    # self.punct = [',', '.', '!', '?', ';', ]
    trash = ('<', '>', '(', ')', '"', '-', '\n',
                  "+", "-", "*", "/", "=", "~", "$", "%", "^", "&", "#", "№", "@", "°", )
    # self.digits = list("1234567890")
    phrasalVerbsDict = getPhrasalVerbsDictFromTxtFile()
    prepositionalVerbs = set()
    non_prepositionalVerbs = dict()
    for line in phrasalVerbsDict:
        words = line.split(" ")
        idxList = [idx for idx, word in enumerate(words) if "some" in word]
        if len(idxList) == 0:
            prepositionalVerbs.add(line)
        elif len(idxList) == 1 and idxList[0] == (len(words) - 1):
             prepositionalVerbs.add(" ".join(words[: idxList[0]]))
        elif (len(idxList) == 1 and idxList[0] != (len(words) - 1)) or len(idxList) == 2:
            needWords = re.split(r" ?some\w+ ?", line)
            # non_prepositionalVerbs.update([(needWords[0], needWords[1]), ])
            if non_prepositionalVerbs.get(needWords[0], -1) == -1:
                non_prepositionalVerbs[needWords[0]] = set()
            non_prepositionalVerbs[needWords[0]].add(needWords[1])

        # c = 0
        # for i in non_prepositionalVerbs.values():
        #     c += len(i)
        # print(c)


    @benchmark()
    def parse(self, text: str) -> Dict[str, Set[str,]]:
        """
        return:
        {
        "noun": {"apple", "tea", "dog", }, "verb": {"go", "read", "take", },  "pronoun": {}, "adjective": {},
        "verb": {}, "auxiliary": {}, "adverb": {}, "preposition": {}, "proper_noun": {},
        "prepositional_verb": {"look after", }, "phrasal_verb": {"throw something away", }
        }
        """
        wordsDict = dict()
        poss = ["noun", "pronoun", "adjective", "verb", "auxiliary", "adverb", "preposition", "proper_noun", ]
        addPoss = ["prepositional_verb", "phrasal_verb"]

        poss.extend(addPoss)

        for pos in poss:
            wordsDict[pos] = set()

        for delim in self.trash:
            text = text.replace(delim, " ")

        while "  " in text:
            text = text.replace("  ", " ")

        doc = self.nlp(text)
        # print(doc)

        # in tokens we have
        # changed prepositional tokens tag name to "preposition"
        # changed verbal tokens tag name to "verb"
        # verbal tokens converted to infinitive form
        # changed noun tokens tag name to "noun"
        # changed adverb tokens tag name to "adverb"
        tokens = [(i.text, i.pos_) for i in doc]
        posMap = {"ADJ": "adjective", "ADP": "preposition", "VERB": "verb", "ADV": "adverb", "AUX": "auxiliary",
                  "NOUN": "noun", "PRON": "pronoun", "PROPN": "proper_noun", }

        assert sorted(list(posMap.values())) == sorted(poss[:-len(addPoss)])

        for idx, token in enumerate(tokens[:]):
            word0, pos0 = token
            word = word0.lower()
            if pos0 in posMap:
                pos = posMap[pos0]
                if pos in ["verb", "auxiliary"]:
                    # verb
                    # verb = nltk.stem.wordnet.WordNetLemmatizer().lemmatize(word, 'v')
                    verb = self.nlp(word)[0].lemma_
                    verb = self.speller(verb)

                    if "'" not in verb:
                        tokens[idx] = (verb, pos)
                        wordsDict[pos].add(verb)

                elif pos == "proper_noun":
                    # proper noun
                    wordsDict[pos].add(word0)
                else:
                    wordsDict[pos].add(word)

            elif pos0 == "PART" and word == "n't":
                tokens[idx] = ("not", pos0)

        # print(tokens)

        wordsDict.update(self.getPharasalVerbs(tokens=tokens))
        return wordsDict

    @benchmark()
    def getPharasalVerbs(self, tokens: List[Tuple[str, ...],]) -> Dict[str, Set]:
        """
        tokens: [('be', 'verb'), ('the', 'DT'), ('person', 'NN'), ('in', 'IN'), ('up', 'adverb'), ]
        """
        verbsDict = {"prepositional_verb": set(), "phrasal_verb": set()}

        # prepositional_verb
        for i in range(len(tokens) - 2):
            verb = tokens[i][0] + " " + tokens[i + 1][0]
            if verb in self.prepositionalVerbs:
                verbsDict["prepositional_verb"].update(self.getPhrasalVerbsFromDict(keyWords=[verb, ]))

            verb = tokens[i][0] + " " + tokens[i + 1][0] + " " + tokens[i + 2][0]
            if verb in self.prepositionalVerbs:
                verbsDict["prepositional_verb"].update(self.getPhrasalVerbsFromDict(keyWords=[verb, ]))
        else:
            verb = tokens[-2][0] + " " + tokens[-1][0]
            if verb in self.prepositionalVerbs:
                verbsDict["prepositional_verb"].update(self.getPhrasalVerbsFromDict(keyWords=[verb, ]))

        # print(verbsDict["prepositional_verb"])

        # phrasal_verb
        phraseIdx0 = -1
        phraseIdx1 = -1
        maxWordsInPhrase = 6
        i = 0
        while i < len(tokens) - 1:
            verb = tokens[i][0]
            if verb in self.non_prepositionalVerbs:
                phraseIdx0 = i + 1
                if tokens[phraseIdx0][0] in self.non_prepositionalVerbs[verb]:
                    phrasalVerbs = self.getPhrasalVerbsFromDict(keyWords=[verb, tokens[phraseIdx0][0]],
                                                                forbidList=verbsDict["prepositional_verb"])
                    verbsDict["phrasal_verb"].update(phrasalVerbs)
                    i += 1
                    continue

                for j in range(1, maxWordsInPhrase + 1):
                    idx = i + j
                    if idx >= len(tokens):
                        break

                    verb1 = tokens[idx][0]

                    if verb1 in self.non_prepositionalVerbs[verb]:
                        phraseIdx1 = idx - 1
                        phrase = [i[0] for i in tokens[phraseIdx0: phraseIdx1 + 1]]
                        phrase = " ".join(phrase)
                        if self.isPhrase(phrase=phrase):
                            phrasalVerbs = self.getPhrasalVerbsFromDict(keyWords=[verb, verb1],
                                                                        forbidList=verbsDict["prepositional_verb"])
                            verbsDict["phrasal_verb"].update(phrasalVerbs)

                            i = idx

            i += 1

        return verbsDict

    def isPhrase(self, phrase: str) -> bool:
        doc = self.nlp(phrase)
        nounPhrases = list(doc.noun_chunks)
        return len(nounPhrases) == 1

    def getPhrasalVerbsFromDict(self, keyWords: List[str,], forbidList: Union[List, Set] = []) -> List[str,]:
        verbs = self.phrasalVerbsDict.keys()
        for word in keyWords:
            verbs = list(filter(lambda x: word in x, verbs))
            # verbs = filter(lambda x: word in x, verbs)

        verbs = list(filter(lambda x: x not in forbidList, verbs))

        return verbs


if __name__ == "__main__":
    tp = TextParser()
    text = """

okay the first thing that we need to do
is install Google Trends in a PowerShell
terming okay so we type pip install
Google Trends it enter successfully
installed now we can close the terminal
here in the code we will do three to ripped
    """
    # "..\_data\parser_temp_files\parsed_file_id=588266453.txt"
    # with open(r"..\resources\phrasalVerbs.txt", "r") as f:
    #     text = f.read()
    #
    wDict = tp.parse(text)
    print(wDict)
    # tp.isPhrase(text)
    # tp.getPhrasalVerbsFromDict(["back", "up"])

