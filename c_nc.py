import mypy
from typing import List, Tuple, Dict
import Mykytea
import re
import numpy as np

def get_morphological_labels(corpus: List[str]) -> List[List[Tuple[str, str]]]:
    """
    Returns a list of morphological labels for each sentence in the corpus.

    Args:
        corpus: A list of sentences.
    Returns:
        A list of morphological labels for each sentence in the corpus.
    """

    opt = "-deftag UNKNOWN!!"
    mk = Mykytea.Mykytea(opt)
    lst = []
    for sentence in corpus:
        for result in mk.getTagsToString(sentence).split():
            lst.append([(result.split("/")[:2])])
    
    return lst

def japanese_filter_regex(tags: List[str]) -> bool:
    """
    Returns whether a word follows termilogy patters in Japanese.

    Args:
        words: A list of word and its tags.
        tags: A list of tags.
    Returns:
        Whether the word is (probably) a terminology.
    """
    tags_concat = "".join(tags)

    # filter1: Noun{2,}
    # filter2: (Prefix | Adv) (Noun | Adj | Suffix)+ Noun+
    # filter3: Prefix Noun+ Suffix

    re_filter = re.compile(u"^(名詞){2,}$|(^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+)$|^((接頭辞)(名詞)+(接尾辞))$") # unicode

    return re_filter.match(tags_concat) is not None # there is a match


def build_frequency_table(corpus: List[str]) -> Dict[str, int]:
    """
    Returns a frequency table of the corpus.

    Args:
        corpus: A list of sentences.
    Returns:
        A frequency table of the corpus.
    """
    freq_table = {}
    for sentence in corpus:
        for word in sentence:
            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1
    return freq_table

def calculate_c_value(words: List[str], nested: bool) -> List[float]:
    """
    Returns the C value for a candidate terminoloy.

    Args:
        word: a candidate terminoloy in more than one word.
        nested: Whether the word is nested.
    Returns:
        The C value for a word.
    """
    if not nested:
        return np.log2(len(words))
        
    else:
        
    


if __name__ == '__main__':
    s = ["仮想関数", "擬似乱数系列", "非同期通信", "全二重接続", "再初期化", "未定義型"]
    print(get_morphological_labels(s))
    #assert get_morphological_labels(s) == [[['今日', '名詞']], [['は', '助詞']], [['い', '形容詞']], [['い', '語尾']], [['天気', '名詞']], [['で', '助動詞']], [['す', '語尾']], [['。', '補助記号']], [['1999', '名詞']], [['年', '名詞']]]
    assert japanese_filter_regex(["名詞", "名詞"])
    assert japanese_filter_regex(["名詞", "名詞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "名詞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "接尾辞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "名詞", "接尾辞"])
