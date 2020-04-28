import os
import platform
import json
from json.decoder import JSONDecodeError
from functools import wraps
from dataclasses import dataclass, astuple, asdict


@dataclass
class FileEntry:
    path: str
    status: str = 'pending'
    digest: str = None
    name_new_txid: str = None
    name_new_nonce: str = None
    name_firstupdate_txid: str = None

    @property
    def name(self):
        return 'poe/{}'.format(self.digest)

    @property
    def can_timestamp(self):
        return not self.name_new_txid

    @property
    def can_publish(self):
        return self.name_new_txid and not self.name_firstupdate_txid


def do_save(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.save()
        return result
    return inner


class FileDatabase:

    @property
    def storage_path(self):
        paths = {
            # FIXME use proper AppData path
            'Windows': r'~\AppData\Roaming\chainsign\storage.json',
            'Darwin': r'~/Library/Application Support/chainsign/storage.json',
            None: '~/.chainsign/storage.json',
            }
        p = paths.get(platform.system(), paths[None])
        p = os.path.expanduser(p)
        directory = os.path.dirname(p)
        os.makedirs(directory, exist_ok=True)
        return p

    def __init__(self):
        try:
            with open(self.storage_path, 'r') as file:
                entries = json.load(file)
                self.files = [FileEntry(**e) for e in entries]
        except (JSONDecodeError, FileNotFoundError):
            self.files = []

    def save(self):
        with open(self.storage_path, 'w') as file:
            json.dump([asdict(f) for f in self.files], file)

    @do_save
    def add_file(self, file_path, status):
        for f in self.files:
            if f.path == file_path:
                return

        fe = FileEntry(
            path=file_path,
            status=status
        )
        self.files.append(fe)

    @do_save
    def set_file_registered(self, file_path, txid, nonce, digest):
        f = self.get_file(file_path)
        if f.name_new_txid:
            return
        f.status = 'registered {}'.format(txid)
        f.name_new_txid = txid
        f.name_new_nonce = nonce
        f.digest = digest

    @do_save
    def set_file_published(self, file_path, txid):
        f = self.get_file(file_path)
        if f.name_firstupdate_txid:
            return
        f.status = 'published {}'.format(txid)
        f.name_firstupdate_txid = txid

    @do_save
    def set_status(self, file_path, status):
        f = self.get_file(file_path)
        if not f:
            raise ValueError(file_path)
        f.status = status

    @do_save
    def del_row(self, row):
        del self.files[row]

    def get_status(self, digest):
        pass

    def get_file(self, path) -> FileEntry:
        for f in self.files:
            if f.path == path:
                return f

    def get_registered(self):
        pass

    def __len__(self):
        return len(self.files)

    def __iter__(self):
        return iter(self.files)

    def __getitem__(self, idx):
        return astuple(self.files[idx])


file_database = FileDatabase()
