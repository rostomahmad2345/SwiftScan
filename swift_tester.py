import unittest
import time
import os
import matplotlib.pyplot as plt

# Importing the core engine
from swift_core import FileTrie


# ==========================================
# Part 1: Unit Testing Suite
# ==========================================
class TestSwiftScanCore(unittest.TestCase):
    """
    Test suite for validating the core functionality, edge cases,
    and algorithmic accuracy of the SwiftScan engine.
    """

    def setUp(self):
        """Bootstraps a controlled testing environment with predefined mock data."""
        self.trie = FileTrie()
        self.dummy_files = [
            ("report.pdf", "C:/docs/report.pdf"),
            ("Project_Final.docx", "C:/work/Project_Final.docx"),
            ("image-2026.png", "C:/pics/image-2026.png"),
            ("a.txt", "C:/a.txt"),
            ("very_long_file_name_test.txt", "C:/very_long_file_name_test.txt")
        ]
        for name, path in self.dummy_files:
            self.trie.insert(name, path)

    def test_exact_match(self):
        """Validates that the engine correctly identifies and retrieves exact string matches."""
        results = self.trie.search("report")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "C:/docs/report.pdf")

    def test_case_insensitivity(self):
        """Ensures the search algorithm handles mixed-case queries accurately."""
        results = self.trie.search("pRoJeCt")
        self.assertTrue(len(results) > 0)

    def test_substring_match(self):
        """Verifies the Suffix Trie's capability to locate substrings within a file name."""
        results = self.trie.search("2026")
        self.assertEqual(results[0], "C:/pics/image-2026.png")

    def test_empty_query(self):
        """Tests system stability against empty string inputs to prevent unexpected crashes."""
        results = self.trie.search("")
        self.assertEqual(results, [])

    def test_non_existent_file(self):
        """Confirms that querying a non-existent file gracefully returns an empty list."""
        results = self.trie.search("gta_v")
        self.assertEqual(results, [])

    def test_ranking_logic(self):
        """
        Evaluates the mathematical ranking algorithm.
        Expected Order: Exact Match (0) > Prefix Match (1) > Substring Match (2).
        """
        trie = FileTrie()
        trie.insert("my_app.exe", "C:/my_app.exe")
        trie.insert("app.js", "C:/app.js")
        trie.insert("application.pdf", "C:/application.pdf")

        results = trie.search("app")

        self.assertTrue("app.js" in results[0])
        self.assertTrue("application.pdf" in results[1])
        self.assertTrue("my_app.exe" in results[2])


# ==========================================
# Part 2: Multi-Scale Performance Benchmark
# ==========================================
def run_comprehensive_benchmark():
    """
    Executes a multi-scale performance benchmark comparing Total Time (Amortized Analysis)
    across 4 different dataset sizes to visualize scalability and system bottlenecks.
    """
    print("\n" + "=" * 60)
    print("Starting Multi-Scale Scalability Benchmark...")
    print("=" * 60)

    # Define the dataset sizes to benchmark system scalability
    file_counts = [10000, 50000, 100000, 200000]
    query = "target"

    # Simulate a user performing 1 to 50 consecutive searches
    query_counts = list(range(1, 51))

    # Configure a 2x2 grid for the Matplotlib dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('SwiftScan Scalability & Amortized Analysis Dashboard', fontsize=16, fontweight='bold', y=0.98)
    axes = axes.flatten()

    for idx, num_files in enumerate(file_counts):
        print(f"\n[{idx + 1}/4] Testing with {num_files:,} mock files...")

        # 1. Generate dummy file paths in memory
        dummy_paths = [f"C:/folder_{i % 100}/file_{i}.txt" for i in range(num_files)]
        dummy_paths.append("C:/target_project.txt")

        # 2. Measure Preprocessing Overhead (SwiftScan Indexing Time)
        trie = FileTrie()
        start_index = time.time()
        for path in dummy_paths:
            trie.insert(os.path.basename(path), path)
        indexing_time = time.time() - start_index
        print(f"   -> Indexing Time (Paid Once): {indexing_time:.4f} sec")

        # 3. Measure single query time for Regular OS Search O(N)
        start_reg = time.time()
        _ = [p for p in dummy_paths if query in os.path.basename(p).lower()]
        reg_search_time = time.time() - start_reg
        print(f"   -> Single Regular Search O(N): {reg_search_time:.4f} sec")

        # 4. Measure single query time for SwiftScan O(L)
        start_trie = time.time()
        _ = trie.search(query)
        trie_search_time = time.time() - start_trie
        print(f"   -> Single SwiftScan Search O(L): {trie_search_time:.4f} sec")

        # 5. Calculate Total Amortized Time over multiple queries
        regular_totals = [q * reg_search_time for q in query_counts]
        swiftscan_totals = [indexing_time + (q * trie_search_time) for q in query_counts]

        # 6. Plot the comparative data on the current subplot
        ax = axes[idx]
        ax.plot(query_counts, regular_totals, label='Regular OS Search O(N)', color='#e74c3c', linewidth=2)
        ax.plot(query_counts, swiftscan_totals, label='SwiftScan O(L)', color='#2ecc71', linewidth=2)

        # 7. Calculate and plot the Breakeven Point if applicable
        if reg_search_time > trie_search_time:
            breakeven = indexing_time / (reg_search_time - trie_search_time)
            ax.axvline(x=breakeven, color='gray', linestyle='--', label=f'Breakeven: ~{int(breakeven)} queries')

        # Subplot aesthetics
        ax.set_title(f"Dataset Size: {num_files:,} Files", fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Searches', fontsize=10)
        ax.set_ylabel('Total Time Elapsed (Seconds)', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)

    # Adjust layout to prevent subplot overlapping
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save the generated dashboard to the local directory
    file_name = 'comprehensive_dashboard.png'
    plt.savefig(file_name, dpi=300)
    print(f"\n[+] All scalability tests complete! Dashboard saved as '{file_name}'.")
    plt.show()


# ==========================================
# Main Execution Entry Point
# ==========================================
if __name__ == '__main__':
    print("Running Unit Tests Suite (Edge Cases & Ranking Logic)...")

    # Execute the test suite; prevent auto-exit to allow benchmark execution
    test_results = unittest.main(argv=[''], exit=False)

    # Proceed to the performance benchmark only if all unit tests pass
    if test_results.result.wasSuccessful():
        run_comprehensive_benchmark()
    else:
        print("\n[!] Error: Fix the failing Unit Tests before running the benchmark.")