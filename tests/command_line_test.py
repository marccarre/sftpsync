from unittest2 import TestCase, main
from tests.test_utilities import FakeStdOut, FakeStdErr, path_for
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
            self.assertEqual(config['force'],     False)
            self.assertEqual(config['preserve'],  False)
            self.assertEqual(config['quiet'],     False)
            self.assertEqual(config['recursive'], False)
            self.assertEqual(config['verbose'],   False)
            self.assertIsNone(config['private_key'])
            self.assertEqual(len(config['ssh_options']), 0)

    def test_configure_force_short_option(self):
        config = configure(['-f'])
        self.assertEqual(config['force'], True)

    def test_configure_force_long_option(self):
        config = configure(['--force'])
        self.assertEqual(config['force'], True)

    def test_configure_preserve_short_option(self):
        config = configure(['-p'])
        self.assertEqual(config['preserve'], True)

    def test_configure_preserve_long_option(self):
        config = configure(['--preserve'])
        self.assertEqual(config['preserve'], True)

    def test_configure_quiet_short_option(self):
        config = configure(['-q'])
        self.assertEqual(config['quiet'], True)

    def test_configure_quiet_long_option(self):
        config = configure(['--quiet'])
        self.assertEqual(config['quiet'], True)

    def test_configure_recursive_short_option(self):
        config = configure(['-r'])
        self.assertEqual(config['recursive'], True)

    def test_configure_recursive_long_option(self):
        config = configure(['--recursive'])
        self.assertEqual(config['recursive'], True)

    def test_configure_verbose_short_option(self):
        config = configure(['-v'])
        self.assertEqual(config['verbose'], True)

    def test_configure_verbose_long_option(self):
        config = configure(['--verbose'])
        self.assertEqual(config['verbose'], True)

    def test_configure_verbose_and_quiet_at_the_same_time(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--quiet', '--verbose'])
                self.assertIn('ERROR: Please provide either -q/--quiet OR -v/--verbose, but NOT both at the same time.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_identity_short_option(self):
        config = configure(['-i', path_for('test_sftp_server_rsa')])
        self.assertIsNotNone(config['private_key'])
        # Verify path components:
        self.assertIn('sftpsync',             config['private_key'])
        self.assertIn('tests',                config['private_key'])
        self.assertIn('test_sftp_server_rsa', config['private_key'])

    def test_configure_identity_long_option(self):
        config = configure(['--identity', path_for('test_sftp_server_rsa')])
        self.assertIsNotNone(config['private_key'])
        # Verify path components:
        self.assertIn('sftpsync',             config['private_key'])
        self.assertIn('tests',                config['private_key'])
        self.assertIn('test_sftp_server_rsa', config['private_key'])

    def test_configure_missing_identity(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--identity'])
                self.assertIn('ERROR: option --identity requires argument', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_empty_identity(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--identity', ''])
                self.assertIn('ERROR: Invalid path: "". Please provide a valid path to your private key.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_non_existing_identity(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--identity', path_for('non_existing_private_key')])
                error_message = err.getvalue()
                self.assertIn('ERROR: Invalid path: "', error_message)
                self.assertIn('non_existing_private_key". Provided path does NOT exist. Please provide a valid path to your private key.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_proxy_command_using_equal_sign(self):
        config = configure(['-o', 'ProxyCommand=nc -X 5 -x localhost:1080 %h %p'])
        self.assertEqual(len(config['ssh_options']), 1)
        self.assertEqual(config['ssh_options']['ProxyCommand'], 'nc -X 5 -x localhost:1080 %h %p')

    def test_configure_ssh_option_proxy_command_using_whitespace(self):
        config = configure(['-o', 'ProxyCommand nc -X 5 -x localhost:1080 %h %p'])
        self.assertEqual(len(config['ssh_options']), 1)
        self.assertEqual(config['ssh_options']['ProxyCommand'], 'nc -X 5 -x localhost:1080 %h %p')

    def test_configure_missing_ssh_option(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o'])
                self.assertIn('ERROR: option -o requires argument', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_empty_ssh_option(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', ''])
                self.assertIn('ERROR: Invalid SSH option: "".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_key_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', '=nc -X 5 -x localhost:1080 %h %p'])
                self.assertIn('ERROR: Invalid SSH option: "=nc -X 5 -x localhost:1080 %h %p".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_value_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'ProxyCommand='])
                self.assertIn('ERROR: Invalid SSH option: "ProxyCommand=', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_key_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', ' nc -X 5 -x localhost:1080 %h %p'])
                self.assertIn('ERROR: Invalid SSH option: " nc -X 5 -x localhost:1080 %h %p".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_value_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'ProxyCommand '])
                self.assertIn('ERROR: Invalid SSH option: "ProxyCommand ', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_unsupported_option_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'User=john'])
                error_message = err.getvalue()
                self.assertIn('ERROR: Unsupported SSH option: "User". Only the following SSH options are currently supported: ProxyCommand.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_unsupported_option_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'User john'])
                error_message = err.getvalue()
                self.assertIn('ERROR: Unsupported SSH option: "User". Only the following SSH options are currently supported: ProxyCommand.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

if __name__ == '__main__':
    main()
