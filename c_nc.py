import mypy/
from typing import List, Tuple, Dict, Union
import Mykytea
import re
import numpy as np

def get_morphological_labels(corpus: List[str]) -> Tuple[List[str], List[str]]:
    """
    Returns the morphological labels and its corresponding word parts of the corpus.

    Args:
        corpus: list of sentences.
    Returns:
        morphological labels: list of morphological labels
        word_parts: list of corresponding words parts
    """

    opt = "-deftag UNKNOWN!!"
    mk = Mykytea.Mykytea(opt)
    morphological_labels: List[List[str]] = []
    word_parts: List[List[str]] = []

    for sentence in corpus:
        morpho_labels_in_sentence = []
        word_parts_in_sentence = []
        for result in mk.getTagsToString(sentence).split():
            word_part, tag = result.split("/")[:2]
            morpho_labels_in_sentence.append(tag)
            word_parts_in_sentence.append(word_part)
        morphological_labels.append(morpho_labels_in_sentence)
        word_parts.append(word_parts_in_sentence)

    return morphological_labels, word_parts

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

    re_jp_term_filter = re.compile(u"^(名詞){2,}$|(^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+)$|^((接頭辞)(名詞)+(接尾辞))$") # unicode

    return re_jp_term_filter.match(tags_concat) is not None # there is a match

def build_frequency_table(morphological_labels: List[List[str]], word_parts: List[List[str]]) -> Dict[str, int]:
    """
    Returns a frequency table of the corpus.

    Args:
        morphological_labels: list of morphological labels
        word_parts: A list of list of word_parts
    Returns:
        A frequency table ouf word_parts in the form of {word: (frequency, word_length)}
    """
    #TODO add katakana words
    #TODO add character-level matching of katakana
    re_jp_term_filter = re.compile(u"^(名詞){2,}$|(^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+)$|^((接頭辞)(名詞)+(接尾辞))$")
    re_partial_jp_term_filter = re.compile(u"^(名詞)+$|^((接頭辞)|(形容詞))$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+$|^(接頭辞)$|^(接頭辞)(名詞)+$|^((接頭辞)(名詞)+(接尾辞))$") 
    """
    test string
        名詞
        名詞名詞
        接頭辞接尾辞
        接頭辞接尾辞名詞
        接頭辞名詞
        接頭辞名詞名詞
        接頭辞副詞
        接頭辞副詞名詞
        接頭辞
        接頭辞名詞
        接頭辞名詞名詞
        接頭辞名詞名詞接尾辞
        形容詞
        形容詞名詞
        形容詞副詞
        形容詞接尾辞
        形容詞接尾辞名詞
    """
    freq_table = {}
    for tags_in_sentence, word_parts_in_sentence in zip(morphological_labels, word_parts):
        tags_possible_term = ""
        word_parts_possible_term = ""
        possible_term_list = []
        word_nums = 0

        for tag, word_part in zip(tags_in_sentence, word_parts_in_sentence):
            tags_possible_term += tag
            word_parts_possible_term += word_part
            word_nums += 1
            if re_jp_term_filter.match(tags_possible_term) is not None:
                possible_term_list.append(word_parts_possible_term)
                if word_parts_possible_term in freq_table:
                    freq_table[word_parts_possible_term] = [freq_table[word_parts_possible_term][0] + 1, freq_table[word_parts_possible_term][1]]
                else:
                    freq_table[word_parts_possible_term] = [1, word_nums]

            if re_partial_jp_term_filter.match(tags_possible_term) is not None:
                    continue
            else:
                # [('仮想関数', 2), ('仮想関数擬似乱数', 1), ('仮想関数擬似乱数系列', 0)]
                for term, count in zip(possible_term_list, range(len(possible_term_list)-1, 0, -1)):
                    freq_table[term] = [freq_table[term][0] + count, freq_table[term][1]]

                possible_term_list = []
                tags_possible_term = ""
                word_parts_possible_term = ""
                word_nums = 0

    return freq_table


def build_containing_term_table(freq_table: Dict[str, int]) -> Dict[str, List[str]]:
    """
    Returns a subterm table of the corpus.

    Args:
        freq_table: A frequency table of word_parts
    Returns:
        A subterm dictionary of {term: [subter1, subterm2, ...]}]} 
    """
    terms = freq_table.keys()
    containing_term_table = {}
    for term in terms:
        containing_term_table[term] = []
        for containing_term in terms:
            if term != containing_term and term in containing_term:
                containing_term_table[term].append(containing_term)
    
    return containing_term_table

def build_cvalue_table(corpus: List[str]) -> Dict[str, float]:
    """
    Returns a cvalue table of the corpus.

    Args:
        corpus: list of sentences
    Returns:
        A cvalue table of {term: cvalue}
    """
    morphological_labels, word_parts = get_morphological_labels(corpus)
    frequency_table = build_frequency_table(morphological_labels, word_parts)
    containing_term_table = build_containing_term_table(frequency_table)
    cvalue_table = {}
    for term in frequency_table:
        
        freqency, num_word = frequency_table[term]
        containing_words = containing_term_table[term]
        is_nested = (len(containing_words) > 0)
        if not is_nested:
            cvalue_table[term] = np.log2(num_word) * freqency
        else:
            total_fb = sum((frequency_table[containing_term][0] for containing_term in containing_term_table[term]))
            cvalue_table[term] = np.log2(num_word) * (freqency - (1 / len(containing_words)) * total_fb)
    
    return cvalue_table

def build_context_words_table(corpus: List[str]) -> Dict[str, List[Union[str, int]]]:
    """
    Returns a context words table of the corpus.
    
    Args:
        corpus: list of sentences
    Returns:t
        context words table of {context_word: list of lists of (term it appears with, its frequency)}
    """
    #TODO: filter non-essential words like "助詞" before building context words table
    re_jp_term_filter = re.compile(u"^(名詞){2,}$|(^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+)$|^((接頭辞)(名詞)+(接尾辞))$")
    re_partial_jp_term_filter = re.compile(u"^(名詞)+$|^((接頭辞)|(形容詞))$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+$|^(接頭辞)$|^(接頭辞)(名詞)+$|^((接頭辞)(名詞)+(接尾辞))$") 

    morphological_labels, word_parts = get_morphological_labels(corpus)
    term_table = build_frequency_table(morphological_labels, word_parts)
    term_total = len(term_table)
    context_words_table = {}

    # add context words *after* the term
    for tags_in_sentence, word_parts_in_sentence in zip(morphological_labels, word_parts):
        
        word_parts_possible_term = ""
        tags_possible_term = ""

        for i in range(len(word_parts_in_sentence)-1):
            cur_tag, cur_word_part = tags_in_sentence[i], word_parts_in_sentence[i]
            next_tag, next_word_part = tags_in_sentence[i+1], word_parts_in_sentence[i+1]
            
            word_parts_possible_term += cur_word_part
            tags_possible_term = cur_tag + next_tag
            
            if word_parts_possible_term in term_table and next_word_part not in term_table:
                if next_tag in ("名詞", "形容詞", "動詞"):
                    if word_parts_possible_term not in context_words_table:
                        context_words_table[next_word_part] = [[word_parts_possible_term, 1]]
                    elif word_parts_possible_term not in context_words_table[next_word_part]:
                        context_words_table[next_word_part][1] += 1

            if re_partial_jp_term_filter.match(tags_possible_term) is not None:
                    continue
            else:
                tags_possible_term = ""
                word_parts_possible_term = ""

    # add context words *before* the term
    for tags_in_sentence, word_parts_in_sentence in zip(morphological_labels, word_parts):
        word_parts_possible_term = ""
        tags_possible_term = ""
        for i in range(len(word_parts_in_sentence)-1, 0, -1):
            cur_tag, cur_word_part = tags_in_sentence[i], word_parts_in_sentence[i]
            prev_tag, prev_word_part = tags_in_sentence[i-1], word_parts_in_sentence[i-1]
            word_parts_possible_term = cur_word_part + word_parts_possible_term
            tags_possible_term = cur_tag + tags_possible_term

            if word_parts_possible_term in term_table and prev_word_part not in term_table:
                if next_tag in ("名詞", "形容詞", "動詞"):
                    if word_parts_possible_term not in context_words_table:
                        context_words_table[prev_word_part] = [[word_parts_possible_term, 1]]
                    elif word_parts_possible_term not in context_words_table[prev_word_part]:
                        context_words_table[prev_word_part][1] += 1

            if re_partial_jp_term_filter.match(tags_possible_term) is not None:
                    continue
            else:
                tags_possible_term = ""
                word_parts_possible_term = ""

    return context_words_table

def build_context_factor_table(corpus: List[str]) -> Dict[str, float]:
    """
    Returns a context factor table for each term.

    Args:
        corpus: list of sentences
    Returns:
        A context factor table of {term: context factor}
    """
    context_words_table = build_context_words_table(corpus)
    morphological_labels, word_parts = get_morphological_labels(corpus)
    freq_table = build_frequency_table(morphological_labels, word_parts)
    num_terms = len(freq_table)
    inverse_context_words_table = {}

    for context_word in context_words_table:
        weight = len(context_words_table[context_word]) / num_terms
        for term, num_frequency in context_words_table[context_word]:
            if term not in inverse_context_words_table:
                inverse_context_words_table[term] = [weight * num_frequency]
            else:
                inverse_context_words_table[term].append(weight * num_frequency)
    
    for term in inverse_context_words_table:
        inverse_context_words_table[term] = sum(inverse_context_words_table[term])
    
    return inverse_context_words_table

def build_nc_value_table(corpus: List[str]) -> Dict[str, float]:
    """
    Returns a nc value table for each term.

    Args:
        corpus: list of sentences
    Returns:
        A nc value table of {term: nc value}
    """
    c_value_table = build_cvalue_table(corpus)
    context_factor_table = build_context_factor_table(corpus)

    nc_value_table = {}
    for term in c_value_table:
        if term not in context_factor_table:
            nc_value_table[term] = 0.8 * c_value_table[term]
        else:
            nc_value_table[term] = 0.8 * c_value_table[term] + 0.2 * context_factor_table[term]
    
    return nc_value_table

def get_kth_best_candidate_terms(corpus: List[str], k: int) -> List[str]:
    """
    Returns the kth best candidate terms.

    Args:
        k: the number of best candidate terms
    Returns:
        A list of k best candidate terms
    """
    nc_value_table = get_nc_value_table(corpus)
    sorted_nc_value_table = sorted(nc_value_table.items(), key=lambda x: x[1], reverse=True)
    return [term for term, nc_value in sorted_nc_value_table[:k]]

if __name__ == '__main__':

    text = ["""頼朝の死後、幕府に仕えた坂東武士（御家人）の権力闘争によって頼朝の嫡流は断絶し、
    その後は北条氏による執権、やがて北条義時の嫡流である得宗が鎌倉幕府の実質的な支配者となった
    武家政権は室町幕府・江戸幕府へと継承された。""", """植物は基本的には組織切片から全体を再生することができる。
    例えばニンジンを5ミリメートル角程度に切り出し、エタノールなどにつけて消毒し、適切な培地に入れて適切な
    （温度・日照などの）条件におけば胚・不定芽などを経て生育し、元のニンジン同様の形になる（組織培養）。"""]
    cvalue_table = build_cvalue_table(text)
    print(cvalue_table)
    print(build_context_words_table(text))
    print(build_context_words_table(["的武家政権"]))

    s = ["仮想関数", "擬似乱数系列", "非同期通信", "全二重接続", "再初期化", "未定義型"]
    print(get_morphological_labels(s))
    #assert get_morphological_labels(s) == [[['今日', '名詞']], [['は', '助詞']], [['い', '形容詞']], [['い', '語尾']], [['天気', '名詞']], [['で', '助動詞']], [['す', '語尾']], [['。', '補助記号']], [['1999', '名詞']], [['年', '名詞']]]
    """
    assert build_frequency_table([['名詞', '名詞', '名詞', '名詞', '名詞', '接頭辞', \
            '名詞', '名詞', '接頭辞', '名詞', '名詞', '名詞', '接頭辞', '名詞', '接尾辞', \
            '接頭辞', '名詞', '接尾辞']], \
            [['仮想', '関数', '擬似', '乱数', '系列', \
            '非', '同期', '通信', '全', '二', '重', '接続', \
            '再', '初期', '化', '未', '定義', '型']]) == \
            {'仮想関数': 4, \
            '仮想関数擬似': 3, \
            '仮想関数擬似乱数': 2, \
            '仮想関数擬似乱数系列': 1, \
            '同期通信': 1, \
            '二重': 2, \
            '二重接続': 1, \
            '未定義型': 0} 
    """
    assert japanese_filter_regex(["名詞", "名詞"])
    assert japanese_filter_regex(["名詞", "名詞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "名詞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "接尾辞"])
    assert japanese_filter_regex(["接頭辞", "名詞", "名詞", "接尾辞"])