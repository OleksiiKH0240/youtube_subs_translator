class Person:
    def __init__(self, id, first_visible_str_idx=0, visible_strs_numb=15):
        self.id = id
        self.words_strs = []
        self.words_set = set()
        self.known_words_dict = dict()
        self.known_words_strs = []
        self.first_visible_str_idx = first_visible_str_idx
        self.visible_strs_numb = visible_strs_numb
        self.split_token = ' - '

    def save_words(self, words_strs):
        self.words_strs = words_strs
        self.words_set = set([i.split(self.split_token)[0] for i in self.words_strs])
        self.first_visible_str_idx = 0

    def change_first_visible_str_idx(self, str_idx):
        poss_first_idx = min(max(0, str_idx), len(self.words_strs) - 1)
        if abs(poss_first_idx - self.first_visible_str_idx) == self.visible_strs_numb:
            self.first_visible_str_idx = poss_first_idx

    def change_visible_strs_numb(self, strs_numb):
        self.visible_strs_numb = strs_numb

    def replace_word_to_known(self, index):
        replaced_word_str = self.words_strs.pop(index)
        self.words_set.remove(replaced_word_str[:replaced_word_str.index(self.split_token)])
        self.known_words_strs.append(replaced_word_str)

        self.known_words_dict.update((replaced_word_str.split(self.split_token),))
        if self.first_visible_str_idx == len(self.words_strs):
            self.change_first_visible_str_idx(self.first_visible_str_idx - self.visible_strs_numb)

    def add_word_to_know(self, word_str):
        pass

    def cross_with_known_words(self):
        return self.words_set & set(self.known_words_dict.keys())

    def cut_off_with_known_words(self):
        self.words_set -= self.cross_with_known_words()
        self.words_strs = list(filter(lambda x: x[:x.index(self.split_token)] in self.words_set,
                                      self.words_strs))

    def get_visible_strs(self):
        try:
            end_idx = self.first_visible_str_idx + self.visible_strs_numb
            if end_idx > len(self.words_strs):
                return self.words_strs[self.first_visible_str_idx:]
            else:
                return self.words_strs[self.first_visible_str_idx: end_idx]

        except Exception as e:
            print('Error in classes.Person.getvisible_strs', e)
            return []

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if type(other) == int:
            return self.id == other
        return self.id == other.id


if __name__ == "__main__":
    pass
