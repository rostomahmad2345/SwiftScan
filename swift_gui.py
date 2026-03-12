import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import platform
import subprocess

# Importing the engines from our core file
from swift_core import FileTrie, ComputerScanner


class SwiftScanApp:
    def __init__(self, parent):
        """Initializes the main application window and backend search engines."""
        self.root = parent
        self.root.title("SwiftScan - High Performance File Search")
        self.root.geometry("900x650")

        # 1. Initialize our Backend Engines
        self.trie_engine = FileTrie()
        self.scanner = ComputerScanner(self.trie_engine)

        self._build_ui()

    def _build_ui(self):
        """Constructs the graphical user interface, including the layout and data table."""
        # --- Top Frame: Folder Selection ---
        top_frame = tk.Frame(self.root, pady=15)
        top_frame.pack(fill="x", padx=20)

        self.btn_scan = ttk.Button(top_frame, text="1. Select Folder to Index", command=self.start_scan_thread)
        self.btn_scan.pack(side="left")

        self.lbl_status = tk.Label(top_frame, text="Status: Waiting for a folder to index...", fg="gray",
                                   font=("Arial", 10))
        self.lbl_status.pack(side="left", padx=15)

        # --- Middle Frame: Search Box ---
        mid_frame = tk.Frame(self.root, pady=10)
        mid_frame.pack(fill="x", padx=20)

        tk.Label(mid_frame, text="2. Search File:", font=("Arial", 12, "bold")).pack(side="left")

        self.entry_search = ttk.Entry(mid_frame, font=("Arial", 12), state="disabled")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=10)

        self.entry_search.bind("<KeyRelease>", self.perform_search)

        # --- Bottom Frame: Treeview (The Data Table) ---
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.scrollbar = ttk.Scrollbar(bottom_frame)
        self.scrollbar.pack(side="right", fill="y")

        columns = ("Name", "Type", "Location", "FullPath")
        self.tree = ttk.Treeview(bottom_frame, columns=columns, show="headings",
                                 displaycolumns=("Name", "Type", "Location"),
                                 yscrollcommand=self.scrollbar.set)

        self.tree.heading("Name", text="File Name", anchor="w")
        self.tree.heading("Type", text="Type", anchor="w")
        self.tree.heading("Location", text="Folder Location", anchor="w")

        self.tree.column("Name", width=250, minwidth=150)
        self.tree.column("Type", width=80, minwidth=50)
        self.tree.column("Location", width=450, minwidth=250)

        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.tree.yview)

        # --- Context Menu (Right-Click) Setup ---
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open File", command=self.open_selected_file)
        self.context_menu.add_command(label="Open File Location", command=self.open_file_location)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Full Path", command=self.copy_file_path)

        # Bindings for Mouse Clicks
        self.tree.bind("<Double-Button-1>", self.open_selected_file)  # Left Double-Click
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-Click

    def start_scan_thread(self):
        """Prompts the user to select a directory and starts indexing in a background thread."""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.lbl_status.config(text=f"Status: Indexing '{folder_path}'... Please wait.", fg="blue")
        self.btn_scan.config(state="disabled")

        threading.Thread(target=self._run_scanner, args=(folder_path,), daemon=True).start()

    def _run_scanner(self, folder_path):
        """Executes the file indexing process and updates the UI upon completion."""
        start_time = time.time()
        self.scanner.scan_directory(folder_path)
        end_time = time.time()

        success_msg = f"Status: Indexed successfully in {end_time - start_time:.2f} sec! You can search now."
        self.lbl_status.config(text=success_msg, fg="green")
        self.entry_search.config(state="normal")
        self.entry_search.focus()

    def perform_search(self, _event=None):
        """Executes the live search query and dynamically updates the results table."""
        query = self.entry_search.get().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not query:
            self.lbl_status.config(text="Status: Waiting for input...", fg="green")
            return

        start_time = time.time()
        results = self.trie_engine.search(query)
        end_time = time.time()

        for path in results:
            file_name = os.path.basename(path)
            name_without_ext, ext = os.path.splitext(file_name)
            folder_location = os.path.dirname(path)

            self.tree.insert("", "end", values=(name_without_ext, ext, folder_location, path))

        self.lbl_status.config(text=f"Found {len(results)} results in {end_time - start_time:.5f} sec", fg="black")

    # --- Feature Methods ---

    def show_context_menu(self, event):
        """Displays the right-click context menu on the selected item."""
        # Identify which row the user right-clicked on
        item = self.tree.identify_row(event.y)
        if item:
            # Select the row visually
            self.tree.selection_set(item)
            # Pop up the menu at the cursor's coordinates
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _get_selected_path(self):
        """Helper method to retrieve the full path of the currently selected item."""
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        return self.tree.item(selected_item[0], "values")[3]

    def open_selected_file(self, _event=None):
        """Opens the selected file using the system's default application."""
        file_path = self._get_selected_path()
        if not file_path: return

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', file_path))
            else:
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            print(f"Could not open file: {e}")

    def open_file_location(self):
        """Opens the directory containing the selected file."""
        file_path = self._get_selected_path()
        if not file_path: return

        folder_path = os.path.dirname(file_path)
        try:
            if platform.system() == 'Windows':
                os.startfile(folder_path)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', folder_path))
            else:
                subprocess.call(('xdg-open', folder_path))
        except Exception as e:
            print(f"Could not open folder: {e}")

    def copy_file_path(self):
        """Copies the full file path to the system clipboard."""
        file_path = self._get_selected_path()
        if not file_path: return

        # Clear the clipboard and append the new path
        self.root.clipboard_clear()
        self.root.clipboard_append(file_path)
        self.root.update()  # Required to finalize the clipboard update on some OS


if __name__ == "__main__":
    main_root = tk.Tk()
    app = SwiftScanApp(main_root)
    main_root.mainloop()