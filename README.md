Module c_nc
===========
Implementation of C-value/NC-value algorithm for unsupervised recognition of
Multi-word terms discussed in the following paper:

Mima, H., & Ananiadou, S. (2000). 
An application and e aluation of the C/NC-value approach 
for the automatic term recognition of multi-word units in Japanese. *Terminology.*
*International Journal of Theoretical and Applied Issues in Specialized Communication*

Functions
---------

    
`build_containing_term_table(freq_table: Dict[str, int]) ‑> Dict[str, List[str]]`
:   Returns a subterm table of the corpus.
    
    Args:
        freq_table: A frequency table of word_parts
    Returns:
        A subterm dictionary of {term: [subter1, subterm2, ...]}]}

    
`build_context_factor_table(corpus: List[str]) ‑> Dict[str, float]`
:   Returns a context factor table for each term.
    
    Args:
        corpus: list of sentences
    Returns:
        A context factor table of {term: context factor}

    
`build_context_words_table(corpus: List[str]) ‑> Dict[str, List[Union[str, int]]]`
:   Returns a context words table of the corpus.
    
    Args:
        corpus: list of sentences
    Returns:t
        context words table of {context_word: list of lists of (term it appears with, its frequency)}

    
`build_cvalue_table(corpus: List[str]) ‑> Dict[str, float]`
:   Returns a cvalue table of the corpus.
    
    Args:
        corpus: list of sentences
    Returns:
        A cvalue table of {term: cvalue}

    
`build_frequency_table(morphological_labels: List[List[str]], word_parts: List[List[str]]) ‑> Dict[str, int]`
:   Returns a frequency table of the corpus.
    
    Args:
        morphological_labels: list of morphological labels
        word_parts: A list of list of word_parts
    Returns:
        A frequency table ouf word_parts in the form of {word: (frequency, word_length)}

    
`build_nc_value_table(corpus: List[str]) ‑> Dict[str, float]`
:   Returns a nc value table for each term.
    
    Args:
        corpus: list of sentences
    Returns:
        A nc value table of {term: nc value}

    
`get_kth_best_candidate_terms(corpus: List[str], k: int) ‑> List[str]`
:   Returns the kth best candidate terms.
    
    Args:
        k: the number of best candidate terms
    Returns:
        A list of k best candidate terms

    
`get_morphological_labels(corpus: List[str]) ‑> Tuple[List[str], List[str]]`
:   Returns the morphological labels and its corresponding word parts of the corpus.
    
    Args:
        corpus: list of sentences.
    Returns:
        morphological labels: list of morphological labels
        word_parts: list of corresponding words parts

    
`japanese_filter_regex(tags: List[str]) ‑> bool`
:   Returns whether a word follows termilogy patters in Japanese.
    
    Args:
        tags: A list of tags.
    Returns:
        Whether the word follows term pattern.

    
`partial_japanese_filter_regex(tags: List[str]) ‑> bool`
:   Returns whether a word follows (partial) termilogy patters in Japanese.
    Used only for testing
    
    Args:
        tags: A list of tags.
    Returns:
        Whether the word follows term pattern partially.