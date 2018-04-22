import hashlib
import copy
import os


class Ed2k:
    """
    Ed2k hash implementation.

    Interface is the same as hashlib.hash objects.
    """

    chunk_size = 9728000

    def __init__(self):
        self._md4_partial = hashlib.new('md4')
        self._md4_final = hashlib.new('md4')
        self._size_total = 0

    @property
    def digest_size(self):
        return self._md4_final.digest_size

    @property
    def block_size(self):
        return self._md4_final.block_size

    def update(self, data):
        pos = 0
        while pos < len(data):
            if not self._size_total % self.chunk_size and self._size_total:
                self._md4_final.update(self._md4_partial.digest())
                self._md4_partial = hashlib.new('md4')

            size = min(len(data) - pos,
                       self.chunk_size - (self._size_total % self.chunk_size))

            self._md4_partial.update(data[pos:pos+size])
            pos += size
            self._size_total += size

    def _finish(self):
        if self._size_total > self.chunk_size:
            tmp = self._md4_final.copy()
            tmp.update(self._md4_partial.digest())
            return tmp
        return self._md4_partial

    def digest(self):
        return self._finish().digest()

    def hexdigest(self):
        return self._finish().hexdigest()

    def copy(self):
        return copy.deepcopy(self)


def file_ed2k(file_path):
    """Calculate Ed2k hash of the file and return it as hex string."""
    ed2k = Ed2k()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            ed2k.update(data)
    return ed2k.hexdigest()


def file_ed2k_link(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_hash = file_ed2k(file_path)
    return ('ed2k://|file|{file_name}|{file_size}|{file_hash}|/'
            .format(**locals()))


if __name__ == '__main__':
    import sys
    for file in sys.argv[1:]:
        print(file_ed2k_link(file))
