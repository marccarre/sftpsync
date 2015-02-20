import os
import sys
from six import StringIO


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
