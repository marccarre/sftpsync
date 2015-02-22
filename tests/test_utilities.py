import os
import sys
from shutil import rmtree
from errno import ENOENT
from stat import S_IRUSR, S_IWUSR
from six import StringIO
from tempfile import mkstemp, mkdtemp


def path_for(filename):
    return os.path.join(current_dir(), filename)

def current_dir():
    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class FakeStdOut(object):
    def __enter__(self):
        self._stream = StringIO()
        self._original_stdout, sys.stdout = sys.stdout, self._stream
        return self._stream
    def __exit__(self, type, value, traceback):
        sys.stdout = self._original_stdout
        self._stream.close()

class FakeStdErr(object):
    def __enter__(self):
        self._stream = StringIO()
        self._original_stderr, sys.stderr = sys.stderr, self._stream
        return self._stream
    def __exit__(self, type, value, traceback):
        sys.stderr = self._original_stderr
        self._stream.close()

class TempFile(object):
    def __enter__(self):
        self._fd, self._path = mkstemp()
        return self._path
    def __exit__(self, type, value, traceback):
        os.close(self._fd)
        os.remove(self._path)

class TempFolder(object):
    def __init__(self):
        self._folder = mkdtemp()
    def _delete_folder(self):
        try:
            rmtree(self._folder)
        except OSError as e:
            if e.errno != ENOENT:  # Other error than 'No such file or directory'.
                raise

class NonReadableFolder(TempFolder):
    def __enter__(self):
        self._chmod  = os.stat(self._folder).st_mode
        os.chmod(self._folder, S_IWUSR)
        return self._folder
    def __exit__(self, type, value, traceback):
        os.chmod(self._folder, self._chmod)
        self._delete_folder()

class NonWritableFolder(TempFolder):
    def __enter__(self):
        self._chmod  = os.stat(self._folder).st_mode
        os.chmod(self._folder, S_IRUSR)
        return self._folder
    def __exit__(self, type, value, traceback):
        os.chmod(self._folder, self._chmod)
        self._delete_folder()
