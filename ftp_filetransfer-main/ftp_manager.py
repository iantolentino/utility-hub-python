# ftp_manager.py
import os
from ftplib import FTP, error_perm

class FTPManager:
    def __init__(self):
        self.ftp = None
        self.connected = False

    def connect(self, host, port=21, username='anonymous', password=''):
        if self.connected:
            self.disconnect()

        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(username, password)
        ftp.set_pasv(True)
        self.ftp = ftp
        self.connected = True
        return ftp.getwelcome()

    def disconnect(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception:
                try:
                    self.ftp.close()
                except Exception:
                    pass
        self.ftp = None
        self.connected = False

    def list_remote(self, path='.'):
        """Return list of file names (simple)."""
        if not self.connected:
            raise RuntimeError("Not connected")

        try:
            items = []
            # Prefer NLST for simple name listing
            items = self.ftp.nlst(path)
        except error_perm as e:
            # Some servers disallow nlst on certain dirs; fallback to LIST then parse
            lines = []
            self.ftp.retrlines(f'LIST {path}', lines.append)
            # Try to extract filenames (last token)
            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    name = ' '.join(parts[8:])
                else:
                    name = parts[-1] if parts else line
                items.append(name)
        return items

    def download(self, remote_path, local_path, callback=None):
        """Download remote_path and save to local_path.
        callback(bytes_transferred) can be used to report progress."""
        if not self.connected:
            raise RuntimeError("Not connected")

        dirname = os.path.dirname(local_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(local_path, 'wb') as f:
            def writer(data):
                f.write(data)
                if callback:
                    callback(len(data))
            self.ftp.retrbinary(f'RETR {remote_path}', writer)

    def upload(self, local_path, remote_path, callback=None):
        """Upload local_path to remote_path.
        callback(bytes_transferred) for progress."""
        if not self.connected:
            raise RuntimeError("Not connected")

        with open(local_path, 'rb') as f:
            def reader(blocksize=8192):
                data = f.read(blocksize)
                return data
            # ftplib expects a file-like object supporting .read, so use storbinary directly:
            f.seek(0)
            def cb(data):
                if callback:
                    callback(len(data))
            self.ftp.storbinary(f'STOR {remote_path}', f, blocksize=8192, callback=cb)
