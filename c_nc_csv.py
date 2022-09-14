import csv
import math
import pickle
import re
from pathlib import Path
from typing import List, Tuple, Dict, Union

from c_nc import build_containing_term_table, build_frequency_table

# changes from the original codes
def get_morphological_labels_from(tokenized_texts: List[str]) -> Tuple[List[str], List[str]]:
    tags: List[List[str]] = []
    tokens: List[List[str]] = []

    tag_pattern = re.compile(r"(.+?/.+?/.+?) ")

    for tokenized_text in tokenized_texts:
        _tags = []
        _tokens = []

        # Don't use tags.split() because each a/b/c may have white spaces.
        for token_and_tags in tag_pattern.findall(tokenized_text):
            token, tag = token_and_tags.split("/")[:2]
            _tags.append(tag)
            _tokens.append(token)
        tags.append(_tags)
        tokens.append(_tokens)

    return tags, tokens


def build_cvalue_table_from(tokenized_texts: List[str]) -> Dict[str, float]:

    # change from the original codes
    morphological_labels, word_parts = get_morphological_labels_from(tokenized_texts)

    frequency_table = build_frequency_table(morphological_labels, word_parts)
    containing_term_table = build_containing_term_table(frequency_table)
    cvalue_table = {}
    for term in frequency_table:

        freqency, num_word = frequency_table[term]
        containing_words = containing_term_table[term]
        is_nested = (len(containing_words) > 0)
        if not is_nested:
            cvalue_table[term] = math.log2(num_word) * freqency
        else:
            total_fb = sum((frequency_table[containing_term][0] for containing_term in containing_term_table[term]))
            cvalue_table[term] = math.log2(num_word) * (freqency - (1 / len(containing_words)) * total_fb)

    return cvalue_table


def build_context_words_table_from(tokenized_texts: List[str]) -> Dict[str, List[Union[str, int]]]:
    re_jp_term_filter = re.compile(u"^(名詞){2,}$|(^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+)$|^((接頭辞)(名詞)+(接尾辞))$")
    re_partial_jp_term_filter = re.compile(u"^(名詞)+$|^((接頭辞)|(形容詞))$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+$|^((接頭辞)|(形容詞))((名詞)|(副詞)|(接尾辞))+(名詞)+$|^(接頭辞)$|^(接頭辞)(名詞)+$|^((接頭辞)(名詞)+(接尾辞))$") 

    # change from the original codes
    morphological_labels, word_parts = get_morphological_labels_from(tokenized_texts)

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


def build_context_factor_table_from(tokenized_texts: List[str]) -> Dict[str, float]:

    # changes from the original codes
    context_words_table = build_context_words_table_from(tokenized_texts)
    morphological_labels, word_parts = get_morphological_labels_from(tokenized_texts)

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


def build_nc_value_table_from(tokenized_texts: List[str]) -> Dict[str, float]:

    # changes from the original codes
    c_value_table = build_cvalue_table_from(tokenized_texts)
    context_factor_table = build_context_factor_table_from(tokenized_texts)

    nc_value_table = {}
    for term in c_value_table:
        if term not in context_factor_table:
            nc_value_table[term] = 0.8 * c_value_table[term]
        else:
            nc_value_table[term] = 0.8 * c_value_table[term] + 0.2 * context_factor_table[term]

    return nc_value_table


def collect_tokenized_texts(path: Path) -> List[str]:
    tokenized_texts = []
    with open(path) as f:
        reader = csv.reader(f)
        # skip a header
        next(reader)
        # each row consists of id and tokenized_text.
        for row in reader:
            tokenized_text = row[1]
            tokenized_texts.append(tokenized_text)
    return tokenized_texts


def extract_terms_from(tokenized_texts: List[str], k: int) -> List[str]:
    nc_value_table = build_nc_value_table_from(tokenized_texts)
    sorted_nc_value_table = sorted(nc_value_table.items(), key=lambda x: x[1], reverse=True)
    extracted_terms = [term for term, nc_value in sorted_nc_value_table[:k]]
    return extracted_terms


def write_results(
    source_csv_path: Path,
    extracted_term_csv_path: Path,
    extracted_term_pkl_path: List[str],
) -> None:

    with open(extracted_term_pkl_path, "rb") as f:
        extracted_terms = pickle.load(f)

    with open(source_csv_path, "r") as fr, open(extracted_term_csv_path, "w") as fw:
        reader = csv.reader(fr)
        writer = csv.writer(fw)

        # header of the output CSV
        writer.writerow(["id", "extracted_terms"])

        for i, input_row in enumerate(reader):

            # header of the input CSV
            if i <= 2:
                continue

            output_row = []
            _extracted_terms = []
            for i, column in enumerate(input_row):
                if i == 0:
                    output_row.append(column)  # id
                else:
                    for term in extracted_terms:
                        if term in column:
                            _extracted_terms.append(term)
                    output_row.append(column)

            writer.writerow(" ".join(output_row))


def get_kth_best_candidate_terms_from_csv(
    source_csv_path: Path,
    tokenized_text_csv_path: Path,
    extracted_term_pkl_path: Path,
    k: int
) -> List[str]:

    tokenized_texts = collect_tokenized_texts(tokenized_text_csv_path)
    extracted_terms = extract_terms_from(tokenized_texts, k)

    with open(extracted_term_pkl_path, "wb") as f:
        pickle.dump(extracted_terms, f)


if __name__ == '__main__':
    source_csv_path = Path("source.csv")
    tokenized_text_csv_path = Path("all_tokenized_text.csv")
    extracted_term_csv_path = Path("extracted_term.csv")
    extracted_term_pkl_path = Path("extracted_term.pkl")

    get_kth_best_candidate_terms_from_csv(
        source_csv_path,
        tokenized_text_csv_path,
        extracted_term_pkl_path,
        1000,
    )

    write_results(
        source_csv_path,
        extracted_term_csv_path,
        extracted_term_pkl_path,
    )
