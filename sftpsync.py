import os
import sys
import getopt
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
    print('Synchronized %s files in %s.' % (files_copied, strftime('%H:%M:%S', gmtime(time() - start_time))))


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

def _parse_socks_version(version='SOCKS5', white_list=PROXY_VERSIONS):
    if version not in white_list:
        raise ValueError('Invalid SOCKS version: "%s". Please choose one of the following values: "%s".' % (version, '", "'.join(white_list)))
    return eval('socks.%s' % version)



ERROR_INVALID_CMD_LINE_ARGS = 2
PROXY_VERSIONS = ['SOCKS4', 'SOCKS5']
OPTIONS = {
}

def usage():
    print('sftpsync.py [-hipqrv] user:password@host:port/path /path/to/local/copy')
    print('Options:')
    print('-h/--help       Prints this!')
    print('-i/--identity identity_file')
    print('                Selects the file from which the identity (private key) for public key authentication is read.')
    print('-p/--preserve:  Preserves modification times, access times, and modes from the original file.')
    print('-q/--quiet:     Quiet mode: disables the progress meter as well as warning and diagnostic messages from ssh(1).')
    print('-r/--recursive: Recursively synchronize entire directories.')
    print('-v/--verbose:   Verbose mode. Causes sftpsync to print debugging messages about their progress. This is helpful in debugging connection, authentication, and configuration problems.')

def get_args(argv):
    try:
        return getopt.getopt(argv, 'h', ['help'])
    except getopt.GetoptError:
        usage()
        sys.exit(ERROR_INVALID_CMD_LINE_ARGS)

def configure(argv):
    opts, args = get_args(argv)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt == '--':
            pass

    if not sftpsync:
        usage()
        sys.exit(ERROR_INVALID_CMD_LINlE_ARGS)
    return sftpsync

def main(argv):
    pass

if __name__ == '__main__':
    main(sys.argv[1:])
