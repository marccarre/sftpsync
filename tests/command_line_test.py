from unittest2 import TestCase, main
from tests.test_utilities import FakeStdOut, FakeStdErr
from sftpsync.command_line import usage, configure

class CommandLineTest(TestCase):

    def test_usage(self):
        with FakeStdOut() as out:
            usage()
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_usage_with_error_message(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                usage('Invalid argument "foo".')
                self.assertIn('ERROR: Invalid argument "foo".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_with_non_existing_short_option(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                with self.assertRaises(SystemExit) as e:
                    configure(['-z'])
                self.assertEqual(e.exception.code, 2)
                self.assertIn('ERROR: option -z not recognized', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_with_non_existing_long_option(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                with self.assertRaises(SystemExit) as e:
                    configure(['--non-existing'])
                self.assertEqual(e.exception.code, 2)
                self.assertIn('ERROR: option --non-existing not recognized', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_help_short_option(self):
        with FakeStdOut() as out:
            with self.assertRaises(SystemExit) as e:
                configure(['-h'])
            self.assertEqual(e.exception.code, 0)
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())        

    def test_configure_help_long_option(self):
        with FakeStdOut() as out:
            with self.assertRaises(SystemExit) as e:
                configure(['--help'])
            self.assertEqual(e.exception.code, 0)
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())        

if __name__ == '__main__':
    main()
