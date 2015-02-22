from unittest2 import TestCase, main
from tests.test_utilities import FakeStdOut, FakeStdErr, NonWritableFolder, NonReadableFolder, path_for
from six import assertRaisesRegex
from getpass import getuser
from sftpsync.command_line import usage, configure
import socks


DEFAULT_ARGS = ['sftp://user:pass@sftp-server.example.com:22/data', path_for('.')]

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
            config = configure([] + DEFAULT_ARGS)
            self.assertEqual(config['force'],     False)
            self.assertEqual(config['preserve'],  False)
            self.assertEqual(config['quiet'],     False)
            self.assertEqual(config['recursive'], False)
            self.assertEqual(config['verbose'],   False)
            self.assertIsNone(config['private_key'])
            self.assertIsNone(config['proxy'])
            self.assertEqual(config['proxy_version'], socks.SOCKS5)
            self.assertEqual(len(config['ssh_options']), 0)

    def test_configure_force_short_option(self):
        config = configure(['-f'] + DEFAULT_ARGS)
        self.assertEqual(config['force'], True)

    def test_configure_force_long_option(self):
        config = configure(['--force'] + DEFAULT_ARGS)
        self.assertEqual(config['force'], True)

    def test_configure_preserve_short_option(self):
        config = configure(['-p'] + DEFAULT_ARGS)
        self.assertEqual(config['preserve'], True)

    def test_configure_preserve_long_option(self):
        config = configure(['--preserve'] + DEFAULT_ARGS)
        self.assertEqual(config['preserve'], True)

    def test_configure_quiet_short_option(self):
        config = configure(['-q'] + DEFAULT_ARGS)
        self.assertEqual(config['quiet'], True)

    def test_configure_quiet_long_option(self):
        config = configure(['--quiet'] + DEFAULT_ARGS)
        self.assertEqual(config['quiet'], True)

    def test_configure_recursive_short_option(self):
        config = configure(['-r'] + DEFAULT_ARGS)
        self.assertEqual(config['recursive'], True)

    def test_configure_recursive_long_option(self):
        config = configure(['--recursive'] + DEFAULT_ARGS)
        self.assertEqual(config['recursive'], True)

    def test_configure_verbose_short_option(self):
        config = configure(['-v'] + DEFAULT_ARGS)
        self.assertEqual(config['verbose'], True)

    def test_configure_verbose_long_option(self):
        config = configure(['--verbose'] + DEFAULT_ARGS)
        self.assertEqual(config['verbose'], True)

    def test_configure_verbose_and_quiet_at_the_same_time(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--quiet', '--verbose'] + DEFAULT_ARGS)
                self.assertIn('ERROR: Please provide either -q/--quiet OR -v/--verbose, but NOT both at the same time.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())


    def test_configure_identity_short_option(self):
        config = configure(['-i', path_for('test_sftp_server_rsa')] + DEFAULT_ARGS)
        self.assertIsNotNone(config['private_key'])
        # Verify path components:
        self.assertIn('sftpsync',             config['private_key'])
        self.assertIn('tests',                config['private_key'])
        self.assertIn('test_sftp_server_rsa', config['private_key'])

    def test_configure_identity_long_option(self):
        config = configure(['--identity', path_for('test_sftp_server_rsa')] + DEFAULT_ARGS)
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
                self.assertRaisesRegex(SystemExit, '2', configure, ['--identity', ''] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid path: "". Please provide a valid path to your private key.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_non_existing_identity(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--identity', path_for('non_existing_private_key')] + DEFAULT_ARGS)
                error_message = err.getvalue()
                self.assertIn('ERROR: Invalid path: "', error_message)
                self.assertIn('non_existing_private_key". Provided path does NOT exist. Please provide a valid path to your private key.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())


    def test_configure_ssh_configuration_short_option(self):
        config = configure(['-F', path_for('test_ssh_config')] + DEFAULT_ARGS)
        self.assertIsNotNone(config['ssh_config'])
        # Verify path components:
        self.assertIn('sftpsync',        config['ssh_config'])
        self.assertIn('tests',           config['ssh_config'])
        self.assertIn('test_ssh_config', config['ssh_config'])

    def test_configure_missing_ssh_configuration(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-F'])
                self.assertIn('ERROR: option -F requires argument', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_empty_ssh_configuration(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-F', ''] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid path: "". Please provide a valid path to your SSH configuration.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_non_existing_ssh_configuration(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-F', path_for('non_existing_ssh_config')] + DEFAULT_ARGS)
                error_message = err.getvalue()
                self.assertIn('ERROR: Invalid path: "', error_message)
                self.assertIn('non_existing_ssh_config". Provided path does NOT exist. Please provide a valid path to your SSH configuration.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())


    def test_configure_ssh_option_proxy_command_using_equal_sign(self):
        config = configure(['-o', 'ProxyCommand=nc -X 5 -x localhost:1080 %h %p'] + DEFAULT_ARGS)
        self.assertEqual(len(config['ssh_options']), 1)
        self.assertEqual(config['ssh_options']['ProxyCommand'], 'nc -X 5 -x localhost:1080 %h %p')

    def test_configure_ssh_option_proxy_command_using_whitespace(self):
        config = configure(['-o', 'ProxyCommand nc -X 5 -x localhost:1080 %h %p'] + DEFAULT_ARGS)
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
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', ''] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SSH option: "".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_key_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', '=nc -X 5 -x localhost:1080 %h %p'] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SSH option: "=nc -X 5 -x localhost:1080 %h %p".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_value_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'ProxyCommand='] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SSH option: "ProxyCommand=', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_key_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', ' nc -X 5 -x localhost:1080 %h %p'] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SSH option: " nc -X 5 -x localhost:1080 %h %p".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_with_empty_value_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'ProxyCommand '] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SSH option: "ProxyCommand ', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_unsupported_option_using_equal_sign(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'User=john'] + DEFAULT_ARGS)
                error_message = err.getvalue()
                self.assertIn('ERROR: Unsupported SSH option: "User". Only the following SSH options are currently supported: ProxyCommand.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_ssh_option_unsupported_option_using_whitespace(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['-o', 'User john'] + DEFAULT_ARGS)
                error_message = err.getvalue()
                self.assertIn('ERROR: Unsupported SSH option: "User". Only the following SSH options are currently supported: ProxyCommand.', error_message)
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_proxy_host(self):
        config = configure(['--proxy', 'proxy-server.example.com'] + DEFAULT_ARGS)
        self.assertEqual(len(config['proxy']), 1)
        self.assertEqual(config['proxy']['host'], 'proxy-server.example.com')

    def test_configure_proxy_user_host(self):
        config = configure(['--proxy', 'anonymous@proxy-server.example.com'] + DEFAULT_ARGS)
        self.assertEqual(len(config['proxy']), 2)
        self.assertEqual(config['proxy']['host'], 'proxy-server.example.com')
        self.assertEqual(config['proxy']['user'], 'anonymous')

    def test_configure_proxy_user_host_port(self):
        config = configure(['--proxy', 'anonymous@proxy-server.example.com:1080'] + DEFAULT_ARGS)
        self.assertEqual(len(config['proxy']), 3)
        self.assertEqual(config['proxy']['host'], 'proxy-server.example.com')
        self.assertEqual(config['proxy']['user'], 'anonymous')
        self.assertEqual(config['proxy']['port'], '1080')

    def test_configure_proxy_user_password_host(self):
        config = configure(['--proxy', 'anonymous:password123@proxy-server.example.com'] + DEFAULT_ARGS)
        self.assertEqual(len(config['proxy']), 3)
        self.assertEqual(config['proxy']['host'], 'proxy-server.example.com')
        self.assertEqual(config['proxy']['user'], 'anonymous')
        self.assertEqual(config['proxy']['pass'], 'password123')

    def test_configure_proxy_user_password_host_port(self):
        config = configure(['--proxy', 'anonymous:password123@proxy-server.example.com:1080'] + DEFAULT_ARGS)
        self.assertEqual(len(config['proxy']), 4)
        self.assertEqual(config['proxy']['host'], 'proxy-server.example.com')
        self.assertEqual(config['proxy']['user'], 'anonymous')
        self.assertEqual(config['proxy']['pass'], 'password123')
        self.assertEqual(config['proxy']['port'], '1080')

    def test_configure_missing_proxy(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--proxy'])
                self.assertIn('ERROR: option --proxy requires argument', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_empty_proxy(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--proxy', ''] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid proxy: "".', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())


    def test_configure_proxy_version_socks_4(self):
        config = configure(['--proxy-version', 'SOCKS4'] + DEFAULT_ARGS)
        self.assertEqual(config['proxy_version'], socks.SOCKS4)

    def test_configure_proxy_version_socks_5(self):
        config = configure(['--proxy-version', 'SOCKS5'] + DEFAULT_ARGS)
        self.assertEqual(config['proxy_version'], socks.SOCKS5)

    def test_configure_missing_proxy_version(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--proxy-version'])
                self.assertIn('ERROR: option --proxy-version requires argument', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_empty_proxy_version(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--proxy-version', ''] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SOCKS proxy version: "". Please choose one of the following values: { SOCKS4, SOCKS5 }.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_invalid_proxy_version(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['--proxy-version', 'SOCKS1337-which-does-not-exist'] + DEFAULT_ARGS)
                self.assertIn('ERROR: Invalid SOCKS proxy version: "SOCKS1337-which-does-not-exist". Please choose one of the following values: { SOCKS4, SOCKS5 }.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())


    def test_configure_arguments_sftp_source_local_destination_user_password_host_port_path(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', '.'])
        self.assertEqual(len(config['source']), 5)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')
        self.assertEqual(config['source']['pass'], 'p4$$w0rd')
        self.assertEqual(config['source']['port'], '22')
        self.assertEqual(config['source']['path'], '/data')
        self.assertEqual(config['destination'], '.')

    def test_configure_arguments_sftp_source_local_destination_user_password_host_port(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:22', '.'])
        self.assertEqual(len(config['source']), 4)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')
        self.assertEqual(config['source']['pass'], 'p4$$w0rd')
        self.assertEqual(config['source']['port'], '22')

    def test_configure_arguments_sftp_source_local_destination_user_password_host(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com', '.'])
        self.assertEqual(len(config['source']), 3)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')
        self.assertEqual(config['source']['pass'], 'p4$$w0rd')

    def test_configure_arguments_sftp_source_local_destination_user_host(self):
        config = configure(['sftp://yoda@sftp-server.example.com', '.'])
        self.assertEqual(len(config['source']), 2)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')

    def test_configure_arguments_sftp_source_local_destination_host(self):
        config = configure(['sftp://sftp-server.example.com', '.'])
        self.assertEqual(len(config['source']), 1)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')

    def test_configure_arguments_sftp_source_local_destination_user_password_host_path(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:/data', '.'])
        self.assertEqual(len(config['source']), 4)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')
        self.assertEqual(config['source']['pass'], 'p4$$w0rd')
        self.assertEqual(config['source']['path'], '/data')

    def test_configure_arguments_sftp_source_local_destination_user_password_host_path_without_colon(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com/data', '.'])
        self.assertEqual(len(config['source']), 4)
        self.assertEqual(config['source']['host'], 'sftp-server.example.com')
        self.assertEqual(config['source']['user'], 'yoda')
        self.assertEqual(config['source']['pass'], 'p4$$w0rd')
        self.assertEqual(config['source']['path'], '/data')

    def test_configure_arguments_sftp_source_local_destination_current_folder(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', '.'])
        self.assertEqual(config['destination'], '.')

    def test_configure_arguments_sftp_source_local_destination_parent_folder(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', '..'])
        self.assertEqual(config['destination'], '..')

    def test_configure_arguments_sftp_source_local_destination_root_folder(self):
        config = configure(['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', path_for('.')])
        self.assertEqual(config['destination'], path_for('.'))

    def test_configure_arguments_sftp_source_local_destination_non_existing_destination_folder(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', '/non/existing/folder'])
                self.assertIn('ERROR: Invalid path. "/non/existing/folder" does NOT exist.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_arguments_sftp_source_local_destination_non_writable_folder(self):
        with NonWritableFolder() as path:
            with FakeStdOut() as out:
                with FakeStdErr() as err:
                    self.assertRaisesRegex(SystemExit, '2', configure, ['sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data', path])
                    self.assertIn('ERROR: Invalid path. "%s" exists but user "%s" does NOT have write access.' % (path, getuser()), err.getvalue())
                    self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_arguments_local_source_sftp_destination_user_password_host_port_path(self):
        config = configure(['.', 'sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data'])
        self.assertEqual(config['source'], '.')
        self.assertEqual(len(config['destination']), 5)
        self.assertEqual(config['destination']['host'], 'sftp-server.example.com')
        self.assertEqual(config['destination']['user'], 'yoda')
        self.assertEqual(config['destination']['pass'], 'p4$$w0rd')
        self.assertEqual(config['destination']['port'], '22')
        self.assertEqual(config['destination']['path'], '/data')

    def test_configure_arguments_local_source_sftp_destination_non_existing_source_folder(self):
        with FakeStdOut() as out:
            with FakeStdErr() as err:
                self.assertRaisesRegex(SystemExit, '2', configure, ['/non/existing/folder', 'sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data'])
                self.assertIn('ERROR: Invalid path. "/non/existing/folder" does NOT exist.', err.getvalue())
                self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

    def test_configure_arguments_local_source_sftp_destination_non_readable_folder(self):
        with NonReadableFolder() as path:
            with FakeStdOut() as out:
                with FakeStdErr() as err:
                    self.assertRaisesRegex(SystemExit, '2', configure, [path, 'sftp://yoda:p4$$w0rd@sftp-server.example.com:22/data'])
                    self.assertIn('ERROR: Invalid path. "%s" exists but user "%s" does NOT have read access.' % (path, getuser()), err.getvalue())
                    self.assertIn('sftpsync.py [OPTION]... SOURCE DESTINATION', out.getvalue())

if __name__ == '__main__':
    main()
