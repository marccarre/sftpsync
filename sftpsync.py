#!/usr/bin/python
import os
from os import linesep
from sys import argv, exit, stderr, stdout
from getopt import getopt, GetoptError
from getpass import getuser
import re
import socks
import socket
import paramiko
from paramiko import SFTPClient, SSHClient, SSHConfig, ProxyCommand
import hashlib
from time import time, gmtime, strftime


def sftp_client(host, port=22, username=None, password=None, private_key=None, proxy_socket=None):
    # Infer as much as possible using current user's SSH configuration:
    config = ssh_config(host)

    # Configure potential SOCKS proxy:
    proxy_command = ProxyCommand(config['proxycommand']) if 'proxycommand' in config else None
    socket = proxy_socket or proxy_command or socket.socket

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if password: 
        # Connect using username and password only:
        ssh.connect(
            hostname = config['hostname'], 
            port     = config['port'] or port, 
            username = config['user'] or username, 
            password = password, 
            sock     = socket
        )
    elif not private_key:
        ssh.load_system_host_keys()
        ssh.connect(
            hostname = config['hostname'], 
            port     = config['port'] or port, 
            username = config['user'] or username, 
            sock     = socket
        )
    else:
        ssh.connect(
            hostname     = config['hostname'], 
            port         = config['port']         or port, 
            username     = config['user']         or username, 
            key_filename = config['identityfile'] or private_key, 
            sock         = socket
        )
    return SFTPClient.from_transport(ssh.get_transport())


def synchronize(host, local_dir, preserve_timestamp=True):
    start_time = time()
    files_copied = 0
    with sftp_client(host) as sftp:
        for remote_file in diff(sftp, local_dir):
            local_file = os.path.join(local_dir, remote_file.filename)
            sftp.get(remote_file, local_file)
            files_copied += 1

            if preserve_timestamp:
                os.utime(local_file, (remote_file.st_utime, remote_file.st_utime))

    # TODO: replace with logger:
    stdout.write('Synchronized %s files in %s.%s' % (files_copied, strftime('%H:%M:%S', gmtime(time() - start_time))), linesep)


def diff(sftp, local_dir, compare_md5_hashes=False):
    local_files = dict((filename, os.stat(filename)) for filename in os.listdir(local_dir))

    for remote_file in sftp.listdir_iter():
        filename = remote_file.filename
        if filename not in local_files:
            yield remote_file
        elif compare_md5_hashes and not same_md5_hashes(filename, sftp):
            yield remote_file
        elif local_files[filename].st_utime < remote_file.st_utime:
            yield remote_file
        else:
            # TODO: Log that file has been skipped.
            continue

def same_md5_hashes(filename, sftp):
    local_checksum  = local_md5(filename)
    remote_checksum = remote_md5(filename, sftp) 
    return local_checksum == remote_checksum

MD5_BLOCK_SIZE = 128

def local_md5(file_path, md5=hashlib.md5(), block_size=8192*MD5_BLOCK_SIZE, end_of_file=b''):
    ''' 
    Compute the provided file's MD5 hash by streaming its content, 
    hence reducing transient memory occupancy if the file is large).
    '''
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), end_of_file):
            md5.update(chunk)
    return md5.hexdigest()

def remote_md5(file_path, sftp):
    with sftp.open(file_path, 'rb') as f:
        return f.check('md5')

def ssh_config(host, path_to_ssh_config='~/.ssh/config'):
    '''
    Returns a dictionnary containing at least {'hostname': <host>}.
    If ~/.ssh/config is present and contains some directives, it will parse them and add the relevant fields to the dictionnary.
    '''
    ssh_config = SSHConfig()
    filepath = os.path.expanduser(path_to_ssh_config)
    if os.path.isfile(filepath):
        ssh_config.parse(open(filepath))
    return ssh_config.lookup(host)  # If empty, returns , so we can consolidate the provided dictionary.

def proxy_socket(host, port=1080, username=None, password=None, version=socks.SOCKS5):
    ''' 
    Create a socket and configure it to connect to the SOCKS proxy.

    IMPORTANT: 
    You need to call the close() method on the provided object once done with it, in order to free up associated resources.
    Alternatively, you can use the Python context manager 'with' to automatically close it, e.g. :
        with proxy_socket(params**) as proxy:
            ...
        # Proxy socket is automatically closed at the end of this block.

    Arguments:
    - host      str    address or hostname of the SOCKS proxy.
    - port:     int    port of the SOCKS proxy (default: 1080).
    - username: str    username to authenticate to the SOCKS proxy (default: None).
    - password: str    password to authenticate to the SOCKS proxy (default: None).
    - version:  enum   version of the SOCKS protocol to use (default: socks.SOCKS5).
    '''
    proxy = socks.socksocket()
    proxy.set_proxy(proxy_type=version, addr=host, port=port, username=username, password=password)
    return proxy


ILLEGAL_ARGUMENTS_ERROR = 2

def error(message):
    stderr.write('ERROR: ' + linesep + message + linesep + linesep)

def usage(error_message=None):
    if (error_message):
        error(error_message)
    stdout.write('Usage:' + linesep + \
        'sftpsync.py [OPTION]... [user[:password]@]host[:[port]/path] /path/to/local/copy' + linesep + linesep + \
        'Defaults:' + linesep + \
        '    user:     anonymous' + linesep + \
        '    password: anonymous' + linesep + \
        '    port:     22' + linesep + \
        '    path:     /' + linesep + linesep + \
        'Options:' + linesep + \
        '-f/--force      Force the synchronization regardless of files\' presence or timestamps.' + linesep + \
        '-h/--help       Prints this!' + linesep + \
        '-i/--identity identity_file' + linesep + \
        '                Selects the file from which the identity (private key) for public key authentication is read.' + linesep + \
        '-o ssh_option' + linesep + \
        '                Can be used to pass options to ssh in the format used in ssh_config(5). This is useful for specifying options for which there is no separate sftpsync command-line flag. For full details of the options listed below, and their possible values, see ssh_config(5).' + linesep + \
        '                    ProxyCommand' + linesep + \
        '-p/--preserve:  Preserves modification times, access times, and modes from the original file.' + linesep + \
        '--proxy [user[:password]@]host[:port]' + linesep + \
        '                SOCKS proxy to use. If not provided, port will be defaulted to 1080.' + linesep + \
        '--proxy-version SOCKS4|SOCKS5' + linesep + \
        '                Version of the SOCKS protocol to use. Default is SOCKS5.' + linesep + \
        '-q/--quiet:     Quiet mode: disables the progress meter as well as warning and diagnostic messages from ssh(1).' + linesep + \
        '-r/--recursive: Recursively synchronize entire directories.' + linesep + \
        '-v/--verbose:   Verbose mode. Causes sftpsync to print debugging messages about their progress. This is helpful in debugging connection, authentication, and configuration problems.' + linesep + linesep
    )

_USER = 'user'
_PASS = 'pass'
_HOST = 'host'
_PORT = 'port'
_PATH = 'path'

_SFTP_REGEX_GROUPS = {
    _USER: '.+?',
    _PASS: '.+?',
    _HOST: '[a-zA-Z0-9_\-\.]+',
    _PORT: '[0-9]{1,5}',
    _PATH: '/.*',
}

def _group(name, regexes=_SFTP_REGEX_GROUPS):
    return '(?P<%s>%s)' % (name, regexes[name])

def _parse_connection_string(connection_string):
    pattern = '^%s?(:%s)?@%s(:%s)%s?$' % (_group(_USER), _group(_PASS), _group(_HOST), _group(_PORT), _group(_PATH))
    match = re.search(pattern, connection_string)
    if match:
        return dict((group, match.group(group)) for group in _SFTP_REGEX_GROUPS.iterkeys())
    return None

def _validate_identity(path):
    if not os.path.exists(path):
        raise ValueError('Invalid path. "%s" does NOT exist. Please provide a valid path to identity file.' % path)
    return path

def _validate_socks_version(socks_version):
    if socks_version not in ['SOCKS4', 'SOCKS5']:
        raise ValueError('Invalid SOCKS version: "%s". Please choose one of the following values: "%s".' % (socks_version, '", "'.join(white_list)))
    return eval('socks.%s' % socks_version)

def _validate_path(path):
    if not os.path.exists(path):
        raise ValueError('Invalid path. "%s" does NOT exist.' % path)
    if not os.access(os.path.dirname(os.path.abspath(path)), os.W_OK):
        raise ValueError('Invalid path. "%s" exist but user "%s" does NOT have write access.' % (path, getuser()))
    return path

def _validate_connection_details(connection_string):
    connection_details = _parse_connection_string(connection_string)
    if not connection_details:
        raise ValueError('Please provide a valid SFTP source. Expected a source of the form [user[:password]@]host[:[port]/path], but got: "%s".' % connection_string)
    return connection_details

def _configure(argv):
    try:
        opts, args = getopt(argv, 'fhi:o:pqrv', ['force', 'help', 'identity=', 'preserve', 'proxy=', 'proxy-version=', 'quiet', 'recursive', 'verbose'])

        # Default options:
        force     = False
        preserve  = False
        quiet     = False
        recursive = False
        verbose   = False
        ssh_options   = []
        identity      = None
        proxy_version = socks.SOCKS5
        proxy         = None

        for opt, value in opts:
            if opt in ('-h', '--help'):
                usage()
                exit()
            if opt in ('-f', '--force'):
                force     = True
            if opt in ('-p', '--preserve'):
                preserve  = True
            if opt in ('-q', '--quiet'):
                quiet     = True
            if opt in ('-r', '--recursive'):
                recursive = True
            if opt in ('-v', '--verbose'):
                verbose   = True
            if opt == '-o':
                ssh_options.append(value)
            if opt in ('-i', '--identity'):
                identity = _validate_identity(value)
            if opt == '--proxy':
                proxy = _parse_connection_string(value)
            if opt == '--proxy-version':
                proxy_version = _validate_socks_version(value)

        if verbose and quiet:
            raise ValueError('Please provide either -q/--quiet OR -v/--verbose, but NOT both at the same time.')

        if len(args) < 2:
            raise ValueError('Please provide a SFTP source AND a local destination. Expected 2 arguments but got %s.' % len(args))
        if len(args) > 2:
            raise ValueError('Please provide JUST a SFTP source AND a local destination. Expected 2 arguments but got %s.' % len(args))
        
        (connection_string, local_path) = args
        connection_details = _validate_connection_details(connection_string)
        local_path = _validate_path(local_path)

        print(connection_details)

        # if not sftpsync:
        #     usage()
        #     exit(ILLEGAL_ARGUMENTS_ERROR)
        # return sftpsync
    except GetoptError as e:
        usage(str(e))
        exit(ILLEGAL_ARGUMENTS_ERROR)
    except ValueError as e:
        usage(str(e))
        exit(ILLEGAL_ARGUMENTS_ERROR)

def main(argv):
    sftpsync = _configure(argv)

if __name__ == '__main__':
    main(argv[1:])
