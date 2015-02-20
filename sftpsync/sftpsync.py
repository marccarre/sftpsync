import os
from paramiko import SSHConfig

def ssh_config(path='~/.ssh/config'):
    '''
    Returns an SSHConfig object containing dictionaries for each hostname.
    Each dictionary contains at least {'hostname': <host>}.
    If ~/.ssh/config is present and contains some directives, it will parse them and add the relevant fields to the dictionnary.
    If provided path does not exist, an empty SSHConfig is returned.
    '''
    ssh_config = SSHConfig()
    if os.path.isfile(path):
        ssh_config.parse(open(path))
    return ssh_config
