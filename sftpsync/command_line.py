import sys
from sys import argv, exit
import os
from os import linesep
from getopt import getopt, GetoptError
import re
import socks


ERROR_ILLEGAL_ARGUMENTS = 2

def usage(error_message=None):
    if error_message:
        sys.stderr.write('ERROR: ' + error_message + linesep)

    sys.stdout.write(linesep.join([
        'Usage:',
        '    sftpsync.py [OPTION]... SOURCE DESTINATION',
        'Pull:',
        '    sftpsync.py [OPTION]... [user[:password]@]host[:port][/path] /path/to/local/copy',
        'Push:',
        '    sftpsync.py [OPTION]... /path/to/local/copy [user[:password]@]host[:port][/path]',
        '',
        'Defaults:',
        '    user:     anonymous',
        '    password: anonymous',
        '    port:     22',
        '    path:     /',
        '',
        'Options:',
        '-f/--force      Force the synchronization regardless of files\' presence or timestamps.',
        '-F config_file  Specifies an alternative per-user configuration file.',
        '                If a configuration file is given on the command line, the system-wide configuration file (/etc/ssh/ssh_config) will be ignored.',
        '                The default for the per-user configuration file is ~/.ssh/config.',
        '-h/--help       Prints this!',
        '-i/--identity identity_file',
        '                Selects the file from which the identity (private key) for public key authentication is read.',
        '-o ssh_option',
        '                Can be used to pass options to ssh in the format used in ssh_config(5). This is useful for specifying options for which there is no separate sftpsync command-line flag.',
        '                For full details of the options listed below, and their possible values, see ssh_config(5).',
        '                    ProxyCommand',
        '-p/--preserve:  Preserves modification times, access times, and modes from the original file.',
        '--proxy [user[:password]@]host[:port]',
        '                SOCKS proxy to use. If not provided, port will be defaulted to 1080.',
        '--proxy-version SOCKS4|SOCKS5',
        '                Version of the SOCKS protocol to use. Default is SOCKS5.',
        '-q/--quiet:     Quiet mode: disables the progress meter as well as warning and diagnostic messages from ssh(1).',
        '-r/--recursive: Recursively synchronize entire directories.',
        '-v/--verbose:   Verbose mode. Causes sftpsync to print debugging messages about their progress. This is helpful in debugging connection, authentication, and configuration problems.',
        ''
    ]))

def configure(argv):
    try:
        # Default configuration:
        config = {
            'force':     False,
            'preserve':  False,
            'quiet':     False,
            'recursive': False,
            'verbose':   False,
            'private_key':   None,
            'proxy':         None,
            'proxy_version': socks.SOCKS5,
            'ssh_config' :   '~/.ssh/config',
            'ssh_options':   {},
        }

        opts, args = getopt(argv, 'fF:hi:o:pqrv', ['force', 'help', 'identity=', 'preserve', 'proxy=', 'proxy-version=', 'quiet', 'recursive', 'verbose'])
        for opt, value in opts:
            if opt in ('-h', '--help'):
                usage()
                exit()

            if opt in ('-f', '--force'):
                config['force']     = True
            if opt in ('-p', '--preserve'):
                config['preserve']  = True
            if opt in ('-q', '--quiet'):
                config['quiet']     = True
            if opt in ('-r', '--recursive'):
                config['recursive'] = True
            if opt in ('-v', '--verbose'):
                config['verbose']   = True
            
            if opt in ('-i', '--identity'):
                config['private_key']    = _validate_private_key_path(value)
            
            if opt == '--proxy':
                config['proxy']          = _validate_and_parse_socks_proxy(value)
            if opt == '--proxy-version':
                config['proxy_version']  = _validate_and_parse_socks_proxy_version(value)

            if opt == '-F':
                config['ssh_config']     = _validate_ssh_config_path(value)
            if opt == '-o':
                k, v = _validate_ssh_option(value)
                config['ssh_options'][k] = v

        if config['verbose'] and config['quiet']:
            raise ValueError('Please provide either -q/--quiet OR -v/--verbose, but NOT both at the same time.')

        return config
    except GetoptError as e:
        usage(str(e))
        exit(ERROR_ILLEGAL_ARGUMENTS)
    except ValueError as e:
        usage(str(e))
        exit(ERROR_ILLEGAL_ARGUMENTS)

def _validate_private_key_path(path):
    if not path:
        raise ValueError('Invalid path: "%s". Please provide a valid path to your private key.' % path)
    if not os.path.exists(path):
        raise ValueError('Invalid path: "%s". Provided path does NOT exist. Please provide a valid path to your private key.' % path)
    return path

def _validate_ssh_config_path(path):
    if not path:
        raise ValueError('Invalid path: "%s". Please provide a valid path to your SSH configuration.' % path)
    if not os.path.exists(path):
        raise ValueError('Invalid path: "%s". Provided path does NOT exist. Please provide a valid path to your SSH configuration.' % path)
    return path

def _validate_ssh_option(option, white_list=['ProxyCommand']):
    key_value = option.split('=', 1) if '=' in option else option.split(' ', 1)
    if not key_value or not len(key_value) == 2:
        raise ValueError('Invalid SSH option: "%s".' % option)
    key, value = key_value
    if not key or not value:
        raise ValueError('Invalid SSH option: "%s".' % option)
    if key not in white_list:
        raise ValueError('Unsupported SSH option: "%s". Only the following SSH options are currently supported: %s.' % (key, ', '.join(white_list)))
    return key, value

_USER = 'user'
_PASS = 'pass'
_HOST = 'host'
_PORT = 'port'

_PATTERNS = {
    _USER: '.+?',
    _PASS: '.+?',
    _HOST: '[a-zA-Z0-9_\-\.]+',
    _PORT: '[0-9]{1,5}',
}

def _group(name, patterns=_PATTERNS):
    return '(?P<%s>%s)' % (name, patterns[name])

_PROXY_PATTERN = '^(%s(:%s)?@)?%s(:%s)?$'      % (_group(_USER), _group(_PASS), _group(_HOST), _group(_PORT))

def _validate_and_parse_socks_proxy(proxy):
    return _validate_and_parse_connection_string(proxy, _PROXY_PATTERN, 'Invalid proxy: "%s".' % proxy)

def _validate_and_parse_connection_string(connection_string, pattern, error_message):
    ''' 
    Parses the provided connection string against the provided pattern into a dictionary, if there is a match, 
    or raises exception if no match.
    ''' 
    match = re.search(pattern, connection_string)
    if not match:
        raise ValueError(error_message)
    return dict((key, value) for (key, value) in match.groupdict().items() if value)

def _validate_and_parse_socks_proxy_version(socks_version, white_list=['SOCKS4', 'SOCKS5']):
    if socks_version not in white_list:
        raise ValueError('Invalid SOCKS proxy version: "%s". Please choose one of the following values: { %s }.' % (socks_version, ', '.join(white_list)))
    return eval('socks.%s' % socks_version)
