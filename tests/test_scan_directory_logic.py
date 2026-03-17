import os
import pytest
from unittest.mock import MagicMock
from source.swift_core import FileTrie,ComputerScanner

def test_scanner_loads_real_files(tmp_path):
    sub_folder = tmp_path / "my_documents"
    sub_folder.mkdir()

    file1 = tmp_path / "hello_world.txt"
    file1.write_text("empty")

    file2 = sub_folder / "second_file.pdf"
    file2.write_text("empty")

    trie = FileTrie()
    scanner = ComputerScanner(trie)

    scanner.scan_directory(str(tmp_path))

    results1 = trie.search("hello")
    results2 = trie.search("second")

    assert str(file1) in results1
    assert str(file2) in results2


def test_scanner_ignores_permission_errors(tmp_path):
    file1 = tmp_path / "system_locked.sys"
    file1.write_text("locked")

    file2 = tmp_path / "normal_file.txt"
    file2.write_text("open")
    mock_trie = MagicMock()

    def fake_insert(file_name , full_path):
        if file_name == "system_locked.sys":
            raise PermissionError("access denied")

    mock_trie.insert.side_effect = fake_insert

    scanner = ComputerScanner(mock_trie)

    scanner.scan_directory(str(tmp_path))

    assert mock_trie.insert.call_count == 2