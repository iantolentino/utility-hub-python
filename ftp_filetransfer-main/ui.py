# ui.py
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ftp_manager import FTPManager

class FTPClientUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple FTP Client")
        self.ftp = FTPManager()

        self.local_dir = os.path.expanduser("~")
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)

        # Connection frame
        conn = ttk.LabelFrame(frm, text="Connection")
        conn.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(conn, text="Host:").grid(row=0, column=0, sticky=tk.W)
        self.host_var = tk.StringVar(value="ftp.dlptest.com")
        ttk.Entry(conn, textvariable=self.host_var, width=25).grid(row=0, column=1)

        ttk.Label(conn, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_var = tk.IntVar(value=21)
        ttk.Entry(conn, textvariable=self.port_var, width=6).grid(row=0, column=3)

        ttk.Label(conn, text="Username:").grid(row=1, column=0, sticky=tk.W)
        self.user_var = tk.StringVar(value="anonymous")
        ttk.Entry(conn, textvariable=self.user_var, width=25).grid(row=1, column=1)

        ttk.Label(conn, text="Password:").grid(row=1, column=2, sticky=tk.W)
        self.pass_var = tk.StringVar(value="")
        ttk.Entry(conn, textvariable=self.pass_var, show="*", width=15).grid(row=1, column=3)

        self.connect_btn = ttk.Button(conn, text="Connect", command=self.connect_pressed)
        self.connect_btn.grid(row=0, column=4, rowspan=2, padx=8)

        # Middle: local and remote panes
        panes = ttk.Frame(frm)
        panes.pack(fill=tk.BOTH, expand=True, pady=6)

        # Local pane
        local_frame = ttk.LabelFrame(panes, text="Local")
        local_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.local_dir_label = ttk.Label(local_frame, text=self.local_dir)
        self.local_dir_label.pack(fill=tk.X, padx=4, pady=2)

        self.local_list = tk.Listbox(local_frame, selectmode=tk.SINGLE)
        self.local_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.local_list.bind("<Double-Button-1>", self.on_local_double)

        local_btns = ttk.Frame(local_frame)
        local_btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(local_btns, text="Change Folder", command=self.change_local_folder).pack(side=tk.LEFT)
        ttk.Button(local_btns, text="Upload →", command=self.upload_selected).pack(side=tk.RIGHT)

        # Remote pane
        remote_frame = ttk.LabelFrame(panes, text="Remote")
        remote_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.remote_cwd_var = tk.StringVar(value=".")
        self.remote_cwd_label = ttk.Label(remote_frame, textvariable=self.remote_cwd_var)
        self.remote_cwd_label.pack(fill=tk.X, padx=4, pady=2)

        self.remote_list = tk.Listbox(remote_frame, selectmode=tk.SINGLE)
        self.remote_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.remote_list.bind("<Double-Button-1>", self.on_remote_double)

        remote_btns = ttk.Frame(remote_frame)
        remote_btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(remote_btns, text="← Download", command=self.download_selected).pack(side=tk.LEFT)
        ttk.Button(remote_btns, text="Refresh", command=self.refresh_remote).pack(side=tk.RIGHT)

        # Status bar
        status = ttk.Frame(frm)
        status.pack(fill=tk.X, padx=4, pady=4)
        self.status_var = tk.StringVar(value="Not connected")
        self.status_lbl = ttk.Label(status, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_lbl.pack(fill=tk.X, expand=True)

        # Populate local list initially
        self.populate_local()

    def change_local_folder(self):
        d = filedialog.askdirectory(initialdir=self.local_dir)
        if d:
            self.local_dir = d
            self.local_dir_label.config(text=self.local_dir)
            self.populate_local()

    def populate_local(self):
        self.local_list.delete(0, tk.END)
        try:
            items = os.listdir(self.local_dir)
            items.sort()
            # Show directories with trailing slash
            for it in items:
                if os.path.isdir(os.path.join(self.local_dir, it)):
                    self.local_list.insert(tk.END, it + os.sep)
                else:
                    self.local_list.insert(tk.END, it)
        except Exception as e:
            self.status_var.set(f"Error reading local dir: {e}")

    def connect_pressed(self):
        if not self.ftp.connected:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            user = self.user_var.get()
            pwd = self.pass_var.get()
            self._set_ui_busy(True)
            self.status_var.set("Connecting...")
            threading.Thread(target=self._connect_thread, args=(host, port, user, pwd), daemon=True).start()
        else:
            self._set_ui_busy(True)
            self.status_var.set("Disconnecting...")
            threading.Thread(target=self._disconnect_thread, daemon=True).start()

    def _connect_thread(self, host, port, user, pwd):
        try:
            welcome = self.ftp.connect(host, port, username=user, password=pwd)
            self._update_ui_after_connect(success=True, welcome=welcome)
        except Exception as e:
            self._update_ui_after_connect(success=False, error=str(e))

    def _disconnect_thread(self):
        try:
            self.ftp.disconnect()
            self._update_ui_after_disconnect()
        except Exception as e:
            self.status_var.set(f"Error disconnecting: {e}")
            self._set_ui_busy(False)

    def _update_ui_after_connect(self, success, welcome=None, error=None):
        def ui():
            self._set_ui_busy(False)
            if success:
                self.connect_btn.config(text="Disconnect")
                self.status_var.set("Connected. " + (welcome or ""))
                self.remote_cwd_var.set(".")
                self.refresh_remote()
            else:
                self.status_var.set("Connect failed: " + (error or ""))
        self.root.after(0, ui)

    def _update_ui_after_disconnect(self):
        def ui():
            self._set_ui_busy(False)
            self.connect_btn.config(text="Connect")
            self.status_var.set("Disconnected")
            self.remote_list.delete(0, tk.END)
        self.root.after(0, ui)

    def _set_ui_busy(self, busy=True):
        # disable connect button while busy, keep window responsive
        state = tk.DISABLED if busy else tk.NORMAL
        self.connect_btn.config(state=state)

    def refresh_remote(self):
        if not self.ftp.connected:
            self.status_var.set("Not connected")
            return
        self.status_var.set("Listing remote files...")
        threading.Thread(target=self._list_remote_thread, daemon=True).start()

    def _list_remote_thread(self):
        try:
            items = self.ftp.list_remote(self.remote_cwd_var.get())
            self.root.after(0, lambda: self._populate_remote(items))
            self.root.after(0, lambda: self.status_var.set("Remote list updated"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"List failed: {e}"))

    def _populate_remote(self, items):
        self.remote_list.delete(0, tk.END)
        items_sorted = sorted(items)
        for it in items_sorted:
            self.remote_list.insert(tk.END, it)

    def on_local_double(self, event):
        sel = self.local_list.curselection()
        if not sel:
            return
        name = self.local_list.get(sel[0])
        # If directory, change folder
        if name.endswith(os.sep):
            new_dir = os.path.join(self.local_dir, name.rstrip(os.sep))
            if os.path.isdir(new_dir):
                self.local_dir = new_dir
                self.local_dir_label.config(text=self.local_dir)
                self.populate_local()

    def on_remote_double(self, event):
        sel = self.remote_list.curselection()
        if not sel:
            return
        name = self.remote_list.get(sel[0])
        # Try to change to directory by CWD; if fails, treat as file
        threading.Thread(target=self._try_cwd_thread, args=(name,), daemon=True).start()

    def _try_cwd_thread(self, name):
        try:
            # attempt cwd to name
            self.ftp.ftp.cwd(name)
            cur = self.ftp.ftp.pwd()
            self.root.after(0, lambda: self.remote_cwd_var.set(cur))
            self.refresh_remote()
        except Exception:
            # probably a file; do nothing
            self.root.after(0, lambda: self.status_var.set(f"Selected remote file: {name}"))

    def upload_selected(self):
        sel = self.local_list.curselection()
        if not sel:
            messagebox.showinfo("Upload", "Select a local file to upload")
            return
        name = self.local_list.get(sel[0])
        if name.endswith(os.sep):
            messagebox.showinfo("Upload", "Please select a file, not a folder")
            return
        local_path = os.path.join(self.local_dir, name)
        remote_name = name  # upload with same filename to current remote dir
        if not self.ftp.connected:
            messagebox.showinfo("Upload", "Not connected")
            return
        self.status_var.set("Uploading...")
        threading.Thread(target=self._upload_thread, args=(local_path, remote_name), daemon=True).start()

    def _upload_thread(self, local_path, remote_name):
        try:
            transferred = 0
            def cb(n):
                nonlocal transferred
                transferred += n
                # update status roughly
                self.root.after(0, lambda: self.status_var.set(f"Uploading... {transferred} bytes"))
            self.ftp.upload(local_path, remote_name, callback=cb)
            self.root.after(0, lambda: self.status_var.set("Upload complete"))
            self.root.after(0, self.refresh_remote)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Upload failed: {e}"))

    def download_selected(self):
        sel = self.remote_list.curselection()
        if not sel:
            messagebox.showinfo("Download", "Select a remote file to download")
            return
        name = self.remote_list.get(sel[0])
        # if user picks a directory-like name, it's safest to attempt; most servers list files only
        local_path = os.path.join(self.local_dir, name)
        if not self.ftp.connected:
            messagebox.showinfo("Download", "Not connected")
            return
        self.status_var.set("Downloading...")
        threading.Thread(target=self._download_thread, args=(name, local_path), daemon=True).start()

    def _download_thread(self, remote_name, local_path):
        try:
            transferred = 0
            def cb(n):
                nonlocal transferred
                transferred += n
                self.root.after(0, lambda: self.status_var.set(f"Downloading... {transferred} bytes"))
            self.ftp.download(remote_name, local_path, callback=cb)
            self.root.after(0, lambda: self.status_var.set(f"Downloaded to {local_path}"))
            self.root.after(0, self.populate_local)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Download failed: {e}"))
