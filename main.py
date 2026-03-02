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

# Hash function
def hash_fn(s: str) -> int:
    h = 0
    for ch in s:
        h = h * 31 + ord(ch)
    return h

# return whether or not a given IntList contains a given integer
def intlist_contains(lst: IntList, n: int) -> bool:
    curr = lst
    while curr is not None:
        if curr.first == n:
            return True
        curr = curr.rest
    return False

# Converts an IntList into a python list
def intlist_to_list(lst: IntList) -> List[int]:
    result = []
    curr = lst
    while curr is not None:
        result.append(curr.first)
        curr = curr.rest
    return result

# find the all the lines that a given word appears in given a WordLinesList
# return None if the word does not appear
def wll_find(wll: WordLinesList, word: str) -> Optional[WordLines]:
    if(wll == None):
        return None
    if(wll.first.word == word):
        return wll.first
    return wll_find(wll.rest, word)


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

# return the bin index of a given word within the scope of the HT
def _bin_index(ht: HashTable, word: str) -> int:
    return hash_fn(word) % hash_size(ht)

# Return whether 'ht' contains a mapping for the given 'word'.
def has_key(ht: HashTable, word: str) -> bool:
    idx = _bin_index(ht, word)
    return wll_find(ht.bins[idx], word) is not None



# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    idx = _bin_index(ht, word)
    entry = wll_find(ht.bins[idx], word)
    if entry is None:
        return []
    return intlist_to_list(entry.lines)

# create a new HashTable of twice the length and copy all data over
def _resize(ht: HashTable) -> None:
    new_size = hash_size(ht) * 2
    new_bins: List[WordLinesList] = [None] * new_size
    for bin_wll in ht.bins:
        curr = bin_wll
        while curr is not None:
            wl = curr.first
            new_idx = hash_fn(wl.word) % new_size
            new_bins[new_idx] = WordLinesNode(wl, new_bins[new_idx])
            curr = curr.rest
    ht.bins = new_bins

# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    idx = _bin_index(ht, word)
    entry = wll_find(ht.bins[idx], word)

    if entry is not None:
        # Word already exists
        if not intlist_contains(entry.lines, line):
            entry.lines = IntNode(line, entry.lines)
    else:
        # New word
        new_wl = WordLines(word=word, lines=IntNode(line, None))
        ht.bins[idx] = WordLinesNode(new_wl, ht.bins[idx])
        ht.count += 1
        if ht.count >= hash_size(ht):
            _resize(ht)

# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    keys = []
    for bin_wll in ht.bins:
        curr = bin_wll
        while curr is not None:
            keys.append(curr.first.word)
            curr = curr.rest
    return keys


# remove punctuation, quation marks and any non alphabetical characters 
# from a given string and make it lowercase, seperate each character into
# its own list item and return
def clean_line(line: str) -> List[str]:
    line = line.replace("'", "")
    for ch in string.punctuation:
        line = line.replace(ch, " ")
    line = line.lower()
    return [t for t in line.split() if t.isalpha()]


# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    concordance = make_hash(128)
    for line_num, line in enumerate(lines, start=1):
        for word in clean_line(line):
            if not has_key(stop_words, word):
                add(concordance, word, line_num)
    return concordance


# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input
# file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    stop_words = make_hash(128)
    with open(stop_words_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if word:
                add(stop_words, word, 0)

    with open(in_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    concordance = make_concordance(stop_words, lines)

    with open(out_file, 'w', encoding='utf-8') as f:
        for word in sorted(hash_keys(concordance)):
            line_nums = sorted(lookup(concordance, word))
            f.write(word + ": " + " ".join(str(n) for n in line_nums) + "\n")


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

    def test_lookup_empty(self):
        self.assertEqual(lookup(make_hash(128), "cat"), [])

    def test_lookup_single(self):
        ht = make_hash(128)
        add(ht, "cat", 3)
        self.assertEqual(lookup(ht, "cat"), [3])

    def test_lookup_multiple_lines(self):
        ht = make_hash(128)
        add(ht, "cat", 1)
        add(ht, "cat", 5)
        add(ht, "cat", 9)
        self.assertEqual(sorted(lookup(ht, "cat")), [1, 5, 9])

    def test_lookup_no_duplicates(self):
        ht = make_hash(128)
        add(ht, "dog", 2)
        add(ht, "dog", 2)
        add(ht, "dog", 2)
        self.assertEqual(len(lookup(ht, "dog")), 1)

    def test_add_increments_count(self):
        ht = make_hash(128)
        add(ht, "apple", 1)
        self.assertEqual(hash_count(ht), 1)

    def test_add_same_word_no_count_change(self):
        ht = make_hash(128)
        add(ht, "apple", 1)
        add(ht, "apple", 2)
        self.assertEqual(hash_count(ht), 1)

    def test_add_multiple_words(self):
        ht = make_hash(128)
        add(ht, "apple", 1)
        add(ht, "banana", 2)
        add(ht, "cherry", 3)
        self.assertEqual(hash_count(ht), 3)

    def test_add_duplicate_line_ignored(self):
        ht = make_hash(128)
        add(ht, "rose", 5)
        add(ht, "rose", 5)
        self.assertEqual(lookup(ht, "rose"), [5])

    def test_resize_all_keys_survive(self):
        ht = make_hash(4)
        for i in range(10):
            add(ht, f"word{i}", i)
        self.assertEqual(hash_count(ht), 10)
        for i in range(10):
            self.assertTrue(has_key(ht, f"word{i}"))

    def test_resize_size_doubles(self):
        ht = make_hash(4)
        add(ht, "a", 1)
        add(ht, "b", 2)
        add(ht, "c", 3)
        add(ht, "d", 4)
        self.assertGreater(hash_size(ht), 4)

    def test_hash_keys_empty(self):
        self.assertEqual(hash_keys(make_hash(128)), [])

    def test_hash_keys_correct(self):
        ht = make_hash(128)
        add(ht, "zebra", 1)
        add(ht, "apple", 2)
        add(ht, "mango", 3)
        self.assertEqual(sorted(hash_keys(ht)), ["apple", "mango", "zebra"])

    def test_hash_keys_no_duplicates(self):
        ht = make_hash(128)
        add(ht, "rose", 1)
        add(ht, "rose", 2)
        add(ht, "rose", 3)
        self.assertEqual(hash_keys(ht), ["rose"])

    def test_clean_line_punctuation(self):
        self.assertEqual(clean_line("Hello, World!"), ["hello", "world"])

    def test_clean_line_apostrophe(self):
        self.assertEqual(clean_line("don't"), ["dont"])

    def test_clean_line_non_alphabet(self):
        self.assertEqual(clean_line("Gr8!"), [])

    def test_clean_line_empty(self):
        self.assertEqual(clean_line(""), [])

    def test_clean_line_double_punct(self):
        self.assertEqual(clean_line("((text))"), ["text"])

    def test_make_concordance_filters_stop_words(self):
        stop_words = make_hash(128)
        for w in ["a", "is", "this"]:
            add(stop_words, w, 0)
        conc = make_concordance(stop_words, ["This is a sample file"])
        self.assertTrue(has_key(conc, "sample"))
        self.assertFalse(has_key(conc, "is"))
        self.assertFalse(has_key(conc, "a"))

    def test_make_concordance_line_numbers(self):
        stop_words = make_hash(128)
        conc = make_concordance(stop_words, ["data file", "more data", "file again"])
        self.assertEqual(sorted(lookup(conc, "data")), [1, 2])
        self.assertEqual(sorted(lookup(conc, "file")), [1, 3])

    def test_make_concordance_blank_lines_counted(self):
        stop_words = make_hash(128)
        conc = make_concordance(stop_words, ["hello world", "", "hello again"])
        self.assertEqual(sorted(lookup(conc, "hello")), [1, 3])

    def test_make_concordance_case_insensitive(self):
        stop_words = make_hash(128)
        conc = make_concordance(stop_words, ["Cat CAT cat"])
        self.assertEqual(len(lookup(conc, "cat")), 1)

    def test_make_concordance_spec_sample(self):
        stop_words = make_hash(128)
        for w in ["a","about","be","by","can","do","i","in",
                  "is","it","of","on","the","this","to","was"]:
            add(stop_words, w, 0)
        lines = [
            "This is a sample data ((text)) file, to be ",
            "processed by your word-concordance program!!!",
            "",
            "A REAL data file is MUCH bigger. Gr8!",
        ]
        conc = make_concordance(stop_words, lines)
        self.assertEqual(sorted(lookup(conc, "data")), [1, 4])
        self.assertEqual(sorted(lookup(conc, "file")), [1, 4])
        self.assertEqual(lookup(conc, "sample"), [1])
        self.assertEqual(lookup(conc, "bigger"), [4])
        self.assertFalse(has_key(conc, "gr8"))
        self.assertFalse(has_key(conc, "a"))


if __name__ == '__main__':
    full_concordance("test_input.txt", "test_stop_words.txt", "test_output.txt")
    unittest.main()