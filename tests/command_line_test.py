from unittest2 import TestCase, main
from tests.test_utilities import FakeStdOut, FakeStdErr
from six import assertRaisesRegex
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
                self.assertRaisesRegex(SystemExit, '2', configure, ['-z'])
                self.assertIn('ERROR: option -z not recognized', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_with_non_existing_long_option(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--non-existing'])
                self.assertIn('ERROR: option --non-existing not recognized', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_help_short_option(self):
        with FakeStdOut() as out:
            self.assertRaisesRegex(SystemExit, '', configure, ['-h'])
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_help_long_option(self):
        with FakeStdOut() as out:
            self.assertRaisesRegex(SystemExit, '', configure, ['--help'])
            self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_defaults(self):
            config = configure([])
            self.assertEqual(config['force'],    False)
            self.assertEqual(config['preserve'], False)

    def test_configure_force_short_option(self):
        config = configure(['-f'])
        self.assertIn('force', config.keys())
        self.assertEqual(config['force'], True)

    def test_configure_force_long_option(self):
        config = configure(['--force'])
        self.assertIn('force', config.keys())
        self.assertEqual(config['force'], True)

    def test_configure_preserve_short_option(self):
        config = configure(['-p'])
        self.assertIn('preserve', config.keys())
        self.assertEqual(config['preserve'], True)

    def test_configure_preserve_long_option(self):
        config = configure(['--preserve'])
        self.assertIn('preserve', config.keys())
        self.assertEqual(config['preserve'], True)

if __name__ == '__main__':
    main()
