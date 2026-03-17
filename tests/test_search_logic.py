import pytest
from sourse.swift_core import FileTrie

@pytest.fixture
def global_trie():
    trie = FileTrie()
    trie.insert("report_2026_final.pdf", "/docs/report_2026_final.pdf")
    trie.insert("cat_photo.png", "/images/cat_photo.png")
    trie.insert("caterpillar.png", "/images/caterpillar.png")
    trie.insert("DATA.csv", "/data/DATA.csv")
    return trie

def test_search_middle_substring(global_trie):
    results = global_trie.search("2026")
    assert "/docs/report_2026_final.pdf" in results

def test_search_suffix_only(global_trie):
    results = global_trie.search(".csv")
    assert "/data/DATA.csv" in results

def test_search_multiple_matches(global_trie):
    results = global_trie.search("cat")
    assert len(results) == 2
    assert "/images/cat_photo.png" in results
    assert "/images/caterpillar.png" in results

def test_search_not_found(global_trie):
    results = global_trie.search("dog")
    assert results == []

def test_search_query_longer_than_file(global_trie):
    results = global_trie.search("caterpillar_extra")
    assert len(results) == 0


@pytest.fixture
def sorting_trie():
    trie = FileTrie()

    # 1. Exact Match (Score 0)
    trie.insert("app.py", "/folder1/app.py")
    trie.insert("app.txt", "/folder1/app.txt")
    trie.insert("app.py", "/folder2/app.py")

    # 2. Starts With (Score 1)
    trie.insert("apple.png", "/folder1/apple.png")
    trie.insert("append.c", "/folder1/append.c")
    trie.insert("applet.py", "/folder1/applet.py")

    # 3. Contains (Score 2)
    trie.insert("my_app.exe", "/folder1/my_app.exe")
    trie.insert("whatsapp.apk", "/folder1/whatsapp.apk")

    return trie


def test_search_sorting_by_relevance_score(sorting_trie):
    results = sorting_trie.search("app")
    assert "app" in results[0]
    assert "app" in results[1]
    assert "app" in results[2]
    assert "apple" in results[3]
    assert "my_app.exe" in results[-2] or "whatsapp.apk" in results[-2]


def test_search_sorting_by_length(sorting_trie):
    results = sorting_trie.search("app")
    apple_index = next(i for i , path in enumerate(results) if "apple.png" in path)
    applet_index = next(i for i , path in enumerate(results) if "applet.py" in path)
    assert apple_index < applet_index

def test_search_sorting_by_extension_and_path(sorting_trie):
    results = sorting_trie.search("app")
    top3 = results[:3]
    assert "/folder1/app.py" == top3[0]
    assert "/folder2/app.py" == top3[1]
    assert "/folder1/app.txt" == top3[2]