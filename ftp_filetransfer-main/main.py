# main.py
import tkinter as tk
from ui import FTPClientUI

def main():
    root = tk.Tk()
    app = FTPClientUI(root)
    root.geometry("800x500")
    root.mainloop()

if __name__ == "__main__":
    main()
