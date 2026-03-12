from typing import Dict, Set, List
import os
import time


class TrieNode:
    """
    Represents a single node (character) in the Prefix Tree.
    """

    def __init__(self):
        # A dictionary mapping a character to its child TrieNode
        self.children: Dict[str, 'TrieNode'] = {}

        # A set to store full file paths that end at this specific node.
        # We use a Set to automatically prevent duplicate paths.
        self.file_paths: Set[str] = set()


class FileTrie:
    """
    The main Prefix Tree engine for indexing and searching file names.
    """

    def __init__(self):
        # The root of the tree starts empty
        self.root = TrieNode()

    def insert(self, file_name: str, file_path: str) -> None:
        """
        Inserts a file name and its corresponding path into the Suffix Trie.

        By generating and inserting all possible suffixes of the file name,
        this method upgrades the standard Prefix Tree to support highly efficient
        substring matching. This ensures the search engine can locate the file
        whether the query matches the beginning, middle, or end of the file name.

        Args:
            file_name (str): The name of the file to be indexed.
            file_path (str): The absolute physical path of the file on the disk.

        Time Complexity:
            $O(L^2)$ where L is the length of the file name, as it processes
            every character of every generated suffix.
        """
        file_name = file_name.lower()

        for i in range(len(file_name)):
            suffix = file_name[i:]
            current_node = self.root

            for char in suffix:
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()
                current_node = current_node.children[char]

            current_node.file_paths.add(file_path)

    def search(self, query: str) -> List[str]:
        """
        Executes a high-performance search and applies an advanced multi-criteria ranking algorithm.

        This method traverses the Suffix Trie to locate all file paths containing the
        query. To provide an optimal User Experience (UX), it employs a sophisticated
        sorting mechanism that evaluates the base file name (excluding extensions) to
        ensure the most relevant results appear first.

        Sorting Hierarchy:
        1. Relevance Score:
           - Score 0: Exact match with the base file name.
           - Score 1: Prefix match (the base name starts with the query).
           - Score 2: Substring match (the query is inside the base name).
           - Score 3: Extension match only (e.g., searching for "pdf").
        2. Base Name Length: Shorter names are prioritized over longer ones.
        3. Alphabetical Order: Alphabetical sorting of the base name (and then extension)
           is used as a tie-breaker for files with identical scores and lengths.

        Args:
            query (str): The search string entered by the user.

        Returns:
            List[str]: A list of absolute physical file paths, meticulously ranked
            for the most intuitive and accurate user results.

        Time Complexity:
            $O(Q + N \log N)$ where Q is the query length (for Trie traversal) and N
            is the total number of matched paths (for sorting the final results).
        """
        if not query:
            return []

        query = query.lower()
        current_node = self.root

        for char in query:
            if char not in current_node.children:
                return []
            current_node = current_node.children[char]

        results: Set[str] = set()
        self._collect_all_paths(current_node, results)

        def sort_key(path: str):
            import os
            # 1. Extract the full name and split the extension
            file_name = os.path.basename(path).lower()
            name_without_ext, ext = os.path.splitext(file_name)

            # 2. Determine the Relevance Score
            if name_without_ext == query or file_name == query:
                score = 0
            elif name_without_ext.startswith(query):
                score = 1
            elif query in name_without_ext:
                score = 2
            else:
                score = 3

                # 3. Calculate length based ONLY on the base name
            name_length = len(name_without_ext)

            # 4. Multi-level Tuple Sorting
            return (score, name_length, name_without_ext, ext, path)

        sorted_results = sorted(list(results), key=sort_key)

        return sorted_results

    def _collect_all_paths(self, node: TrieNode, results: Set[str]) -> None:
        """
        A recursive helper function (Depth-First Search) to gather all file paths
        from the current node and all its descending children.
        """
        # Base case / Current step: Add paths stored at the current node (if any)
        if node.file_paths:
            results.update(node.file_paths)

        # Recursive step: Visit all children of the current node
        for child_node in node.children.values():
            self._collect_all_paths(child_node, results)



class ComputerScanner:
    """
    Acts as the 'Eyes' of the search engine. It scans the entire hard drive
    and feeds file names and paths into the FileTrie (The Brain).
    """

    def __init__(self, trie_engine):
        # We link the scanner to our Trie data structure
        self.trie = trie_engine

    def scan_directory(self, root_path: str) -> None:
        """
        Traverses the whole computer starting from a root directory (e.g., 'C:\\').
        """
        print(f"Scanning the entire computer starting from: {root_path}")
        print("Please wait, this might take a few seconds depending on your drive size...")

        # os.walk will dig into every single folder on your computer
        for current_folder, sub_folders, files in os.walk(root_path):
            for file_name in files:
                try:
                    # Construct the full physical path on the computer
                    full_path = os.path.join(current_folder, file_name)

                    # Feed the file name and its full path into our Trie tree
                    self.trie.insert(file_name, full_path)

                except PermissionError:
                    # Operating systems block access to certain system files.
                    # We simply ignore them and continue scanning.
                    continue
                except Exception as e:
                    # Catch any other unexpected errors so the program doesn't crash
                    pass

        print("Scanning completed successfully! The Trie is now fully loaded.")



if __name__ == "__main__":
    # 1. Initialize the Search Engine (The Brain)
    fast_trie_engine = FileTrie()

    # 2. Initialize the Scanner (The Eyes)
    computer_scanner = ComputerScanner(fast_trie_engine)

    # 3. Scan a specific directory or the whole drive
    # (Change this path to a specific folder first to test it quickly)
    folder_to_scan = "C:\\Users"  # Example for Windows. Use '/' for Mac/Linux

    start_scan_time = time.time()
    computer_scanner.scan_directory(folder_to_scan)
    end_scan_time = time.time()
    print(f"Indexing finished in {end_scan_time - start_scan_time:.2f} seconds.\n")

    # 4. Interactive Search Loop
    while True:
        user_query = input("Enter a file name to search (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        start_search_time = time.time()
        # The magic happens here!
        found_files = fast_trie_engine.search(user_query)
        end_search_time = time.time()

        print(f"\nFound {len(found_files)} results in {end_search_time - start_search_time:.5f} seconds:")

        # Display up to 10 results to avoid cluttering the screen
        for path in found_files[:10]:
            print(f" -> {path}")
        if len(found_files) > 10:
            print(f" ... and {len(found_files) - 10} more results.")
        print("-" * 40)

