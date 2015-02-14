from unittest2 import TestCase, main
from test_utilities import FakeStdOut, FakeStdErr
from sftpsync.command_line import usage

class CommandLineTest(TestCase):

    def test_print_usage(self):
        with FakeStdOut() as out:
            usage()
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_print_usage_with_error_message(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                usage('Invalid argument "foo".')
                self.assertIn('ERROR: Invalid argument "foo".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

if __name__ == '__main__':
    main()

