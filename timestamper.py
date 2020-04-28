from datetime import datetime
import json
import hashlib
import sys
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from utils import rpcurl_from_config


class Timestamper(object):
    """Basic timestamping interface"""

    def verify(self, digest):
        """Checks if digest (hash) is present in selected blockchain and returns
        its timestamp and (unique) transaction hash/id in which it has been
        announced. Returns None if it has not been found."""
        raise NotImplementedError

    def register(self, digest):
        """Registers POE of POE :^)"""
        raise NotImplementedError

    def publish(self, name, reg_txid, nonce):
        """Publishes digest onto selected blockchain and returns transaction
        hash/id (which should match with one reported by verify call)"""
        raise NotImplementedError

    def hash_file(self, fd):
        """Returns sha256 hash of provided open fd."""

        filehash = hashlib.sha256()

        for chunk in iter(lambda: fd.read(8192), b""):
            filehash.update(chunk)

        return filehash.hexdigest()

    def verify_file(self, fd):
        """Verifies file from open fd using sha256."""

        return self.verify(self.hash_file(fd))

    def register_file(self, fd):
        """Publishes file from open fd using sha256."""
        digest = self.hash_file(fd)
        reg_txid, nonce = self.register(digest)
        return reg_txid, nonce, digest


class NamecoinTimestamper(Timestamper):
    """Simple Namecoin proof-of-existence timestamper implementation based on
    poe/ identity prefix.
    """

    IDENTITY = 'poe/{}'

    def __init__(self, url='http://127.0.0.1:8336'):
        self.client = AuthServiceProxy(url)

    def verify(self, digest):
        """Namecoin poe/ verification implementation"""

        name = self.IDENTITY.format(digest)
        try:
            hist = self.client.name_history(name)
            txid = hist[0]['txid']
            pending = False
        except JSONRPCException as exc:
            if exc.code == -4:
                hist_pending = self.client.name_pending(name)
                if not hist_pending:
                    return
                txid = hist_pending[0]['txid']
                pending = True
            else:
                # FIXME maybe?
                if str(exc).split(': ')[0] == '-4':
                    return None
                raise
        if not txid:
            return
        tx = self.client.gettransaction(txid)
        return {
            'txid': txid,
            'timestamp': datetime.utcfromtimestamp(tx['time']),
            'pending': pending
        }

    def register(self, digest):
        """Namecoin poe/ publishing implementation"""

        name = self.IDENTITY.format(digest)
        reg_txid, nonce = self.client.name_new(name)

        return reg_txid, nonce

    def publish(self, name, nonce, new_txid):
        data = json.dumps({
            'ver': 0,
            })
        txid = self.client.name_firstupdate(name, nonce, new_txid, data)
        return txid


def main():
    ts = NamecoinTimestamper(rpcurl_from_config('namecoin', 'http://127.0.0.1:8336/'))

    for f in sys.argv[1:]:
        with open(f, 'rb') as fd:
            timestamp = ts.verify_file(fd)

            if timestamp:
                print('File {} found at: {}'.format(f, timestamp['timestamp']))
            else:
                print('File {} not found'.format(f))


if __name__ == "__main__":
    main()
