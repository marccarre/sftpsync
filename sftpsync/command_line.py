from os import linesep
import sys

def usage(error_message=None):
    if error_message:
        sys.stderr.write(u'ERROR: ' + error_message + linesep)

    sys.stdout.write(
        u'Usage:' + linesep + \
        '    sftpsync.py [OPTION]... SOURCE DESTINATION' + linesep + \
        'Pull:' + linesep + \
        '    sftpsync.py [OPTION]... [user[:password]@]host[:[port]/path] /path/to/local/copy' + linesep + \
        'Push:' + linesep + \
        '    sftpsync.py [OPTION]... /path/to/local/copy [user[:password]@]host[:[port]/path]' + linesep + linesep + \

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