import pytest
from source.swift_core import FileTrie

@pytest.fixture
def trie():
    return FileTrie()


def test_insert_simple(trie):
    name = "project.py"
    path = '/home/rostom/project.py'
    trie.insert(name, path)
    results = trie.search("project")
    assert path in results

def test_insert_same_name(trie):
    name = "cat.png"
    path1 = '/home/rostom/cat.png'
    path2 = '/home/desktop/cat.png'
    trie.insert(name, path1)
    trie.insert(name, path2)
    results = trie.search("cat")
    assert len(results) == 2
    assert path1 in results
    assert path2 in results


def test_insert_exact_duplicate(trie):
    name = "cat.png"
    path = "/home/cat.png"
    trie.insert(name, path)
    trie.insert(name, path)
    results = trie.search("cat")
    assert len(results) == 1

def test_insert_suffix_match(trie):
    name = 'homework.pdf'
    path = '/home/rostom/homework.pdf'
    trie.insert(name, path)
    results = trie.search("work")
    assert path in results

def test_insert_with_special_characters(trie):
    name = 'class_1'
    path = '/home/rostom/class_1.pdf'
    trie.insert(name, path)
    results = trie.search("_1")
    assert path in results

def test_insert_case_insensitivity(trie):
    name1= 'CAT.png'
    name2 = 'cat.png'
    path = '/home/rostom/CAT.png'
    trie.insert(name1, path)
    trie.insert(name2, path)
    result1 = trie.search("cat")
    result2 = trie.search("CAT")
    assert set(result1) == set(result2)

def test_insert_hidden_file(trie):
    name = ".secret"
    path = '/home/rostom/.secret'
    trie.insert(name, path)
    results = trie.search(".secret")
    assert path in results

def test_insert_empty_name_handling(trie):
    name = ''
    path = ''
    trie.insert(name, path)
    results = trie.search(".")
    assert results == []

def test_insert_very_long_name(trie):
    name = "a"*200
    path = f'/home/rostom/{name}.png'
    trie.insert(name, path)
    results = trie.search("a")
    assert path in results

def test_insert_overlapping_names(trie):
    name1 = 'test'
    name2 = 'testing'
    path1 = '/home/rostom/test.py'
    path2 = '/home/desktop/testing.py'
    trie.insert(name1, path1)
    trie.insert(name2, path2)
    shared_results = trie.search("test")
    assert len(shared_results) == 2
    assert path1 in shared_results
    assert path2 in shared_results
    long_results = trie.search("testing")
    assert len(long_results) == 1
    assert path1 not in long_results
    assert path2 in long_results