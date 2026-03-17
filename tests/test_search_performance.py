import time
import pytest
from sourse.swift_core import FileTrie


def test_search_performance():
    trie = FileTrie()
    for i in range(10000):
        trie.insert(f'document{i}.txt' , f'/home/rostom/documents/document{i}.txt')
    trie.insert("goal.png" , '/home/rostom/goal.png')
    start_time = time.perf_counter()
    results = trie.search("goal")
    end_time = time.perf_counter()
    duration = (end_time - start_time)*1000
    print(f"\n[Performance] Search in 10,000 files took: {duration:.4f} ms")

    assert duration < 5.0 , f"Performance Drop! Search took {duration:.2f} ms"