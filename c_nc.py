import mypy
from typing import List, Tuple
import Mykytea
import re

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

def japanese_filter_regex(word_with_tags: List[List[str], List[str]]) -> bool:
    """
    Returns whether a word follows termilogy patters in Japanese.

    Args:
        word_with_tags: A list of word and its tags.
    Returns:
        Whether the word is (probably) a terminology.
    """

    return re.match(r"[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF]", word) is not None

def calculate_c_value(corpus: List[str]) -> List[float]:
    pass

if __name__ == '__main__':
    s = ["今日はいい天気です。", "1999年"]
    print(conduct_morphological_analysis(s))