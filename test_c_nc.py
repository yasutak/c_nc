# -*- coding: utf-8 -*-
import unittest
from c_nc import *

text = ["""頼朝の死後、幕府に仕えた坂東武士（御家人）の権力闘争によって頼朝の嫡流は断絶し、
その後は北条氏による執権、やがて北条義時の嫡流である得宗が鎌倉幕府の実質的な支配者となった
武家政権は室町幕府・江戸幕府へと継承された。""", """植物は基本的には組織切片から全体を再生することができる。
例えばニンジンを5ミリメートル角程度に切り出し、エタノールなどにつけて消毒し、適切な培地に入れて適切な
（温度・日照などの）条件におけば胚・不定芽などを経て生育し、元のニンジン同様の形になる（組織培養）。"""]

class SimpleTest(unittest.TestCase):
    
    def test_get_morphological_labels(self):
        s = ["仮想関数", "擬似乱数系列", "非同期通信", "全二重接続", "再初期化", "未定義型"]
        assert get_morphological_labels(s) ==([['名詞', '名詞'],
                                                ['名詞', '名詞', '名詞'],
                                                ['接頭辞', '名詞', '名詞'],
                                                ['接頭辞', '名詞', '名詞', '名詞'],
                                                ['接頭辞', '名詞', '接尾辞'],
                                                ['接頭辞', '名詞', '接尾辞']],
                                                [['仮想', '関数'],
                                                ['擬似', '乱数', '系列'],
                                                ['非', '同期', '通信'],
                                                ['全', '二', '重', '接続'],
                                                ['再', '初期', '化'],
                                                ['未', '定義', '型']])

    def test_japanese_filter_regex(self):
        assert japanese_filter_regex(["名詞", "名詞"])
        assert japanese_filter_regex(["名詞", "名詞"])
        assert japanese_filter_regex(["接頭辞", "名詞", "名詞"])
        assert japanese_filter_regex(["接頭辞", "名詞", "接尾辞"])
        assert japanese_filter_regex(["接頭辞", "名詞", "名詞", "接尾辞"])

    def test_partial_japanese_filter_regex(self):
        assert partial_japanese_filter_regex(["名詞"])
        assert partial_japanese_filter_regex(["名詞名詞"])
        assert partial_japanese_filter_regex(["接頭辞接頭辞"])
        assert partial_japanese_filter_regex(["頭辞接尾辞名詞"])
        assert partial_japanese_filter_regex(["接頭辞名詞"])
        assert partial_japanese_filter_regex(["接頭辞名詞名詞"])
        assert partial_japanese_filter_regex(["接頭辞名詞名詞"])
        assert partial_japanese_filter_regex(["接頭辞名詞名詞接尾辞"])
        assert partial_japanese_filter_regex(["接尾辞副詞"])
        assert partial_japanese_filter_regex(["接尾辞副詞名詞"])
        assert partial_japanese_filter_regex(["接尾辞副詞名詞名詞"])
        assert partial_japanese_filter_regex(["接頭辞"])
        assert partial_japanese_filter_regex(["接頭辞名詞"])
        assert partial_japanese_filter_regex(["形容詞"])
        assert partial_japanese_filter_regex(["形容詞名詞"])
        assert partial_japanese_filter_regex(["形容詞副詞"])
        assert partial_japanese_filter_regex(["形容詞接尾辞"])
        assert partial_japanese_filter_regex(["形容詞接尾辞名詞"])

    def test_frequency_table(self):
        morphological_labels, word_parts = get_morphological_labels(text)
        build_frequency_table(morphological_labels, word_parts) == \
        {'坂東武士': [1, 2], '権力闘争': [1, 2], '北条義時': [1, 2], '鎌倉幕府': [1, 2], '武家政権': [1, 2], '室町幕府': [1, 2], '江戸幕府': [1, 2], '組織切片': [1, 2], '5ミリメートル': [3, 2], '5ミリメートル角': [2, 3], '5ミリメートル角程度': [1, 4], '不定芽': [1, 2], '組織培養': [1, 2]}

    def test_build_context_words_table(self):
        assert build_context_words_table(text) == \
            {'角': [['5ミリメートル', 1]], '程度': [['5ミリメートル角', 1]]}
        
    def test_build_nc_table(self):
        assert build_nc_value_table(text) == \
            {'坂東武士': 0.8,
                '権力闘争': 0.8,
                '北条義時': 0.8,
                '鎌倉幕府': 0.8,
                '武家政権': 0.8,
                '室町幕府': 0.8,
                '江戸幕府': 0.8,
                '組織切片': 0.8,
                '5ミリメートル': 1.2153846153846155,
                '5ミリメートル角': 1.2833546159615403,
                '5ミリメートル角程度': 1.6,
                '不定芽': 0.8,
                '組織培養': 0.8}

    def test_get_kth_best_candidate(self):
        assert get_kth_best_candidate_terms(text, 20) == \
            ['5ミリメートル角程度',
                '5ミリメートル角',
                '5ミリメートル',
                '坂東武士',
                '権力闘争',
                '北条義時',
                '鎌倉幕府',
                '武家政権',
                '室町幕府',
                '江戸幕府',
                '組織切片',
                '不定芽',
                '組織培養']

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(SimpleTest))
  return suite

if __name__ == '__main__':
    unittest.main()