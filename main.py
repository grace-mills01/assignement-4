from typing import *
from dataclasses import dataclass
import unittest
import sys
import string

sys.setrecursionlimit(10**6)


@dataclass(frozen=True)
class IntNode:
    first: int
    rest: "IntList"


IntList = Union[None, IntNode]


@dataclass
class WordLines:
    word: str
    lines: IntList


@dataclass(frozen=True)
class WordLinesNode:
    first: WordLines
    rest: "WordLinesList"


WordLinesList = Union[None, WordLinesNode]


@dataclass
class HashTable:
    bins: List[WordLinesList]
    count: int


# Hash Function
def hash_fn(s: str) -> int:
    h = 0
    for ch in s:
        h = h * 31 + ord(ch)
    return h


# Make a fresh hash table with the given number of bins 'size',
# containing no elements.
def make_hash(size: int) -> HashTable:
    return HashTable(bins=[None] * size, count=0)


# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return len(ht.bins)


# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count


# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    idx = hash_fn(word) % hash_size(ht)
    curr = ht.bins[idx]
    while curr is not None:
        if curr.first.word == word:
            return True
        curr = curr.rest
    return False


# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    pass


# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    pass


# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    pass


# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    pass


# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input
# file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    pass


class Tests(unittest.TestCase):
    # hash_fn
    def test_hash_fn_empty(self):
        self.assertEqual(hash_fn(""), 0)

    def test_hash_fn_single_char(self):
        self.assertEqual(hash_fn("a"), ord("a"))

    def test_hash_fn_two_chars(self):
        self.assertEqual(hash_fn("ab"), 97 * 31 + 98)

    def test_hash_fn_consistent(self):
        self.assertEqual(hash_fn("hello"), hash_fn("hello"))

    def test_hash_fn_different_words(self):
        self.assertNotEqual(hash_fn("cat"), hash_fn("dog"))

    # make_hash / hash_size / hash_count
    def test_make_hash_size(self):
        self.assertEqual(hash_size(make_hash(128)), 128)

    def test_make_hash_count(self):
        self.assertEqual(hash_count(make_hash(128)), 0)

    def test_make_hash_bins_are_none(self):
        ht = make_hash(4)
        self.assertTrue(all(b is None for b in ht.bins))

    # has_key
    def test_has_key_empty(self):
        self.assertFalse(has_key(make_hash(128), "hello"))

    def test_has_key_after_add(self):
        ht = make_hash(128)
        add(ht, "hello", 1)
        self.assertTrue(has_key(ht, "hello"))

    def test_has_key_missing(self):
        ht = make_hash(128)
        add(ht, "hello", 1)
        self.assertFalse(has_key(ht, "world"))


if __name__ == "__main__":
    unittest.main()
