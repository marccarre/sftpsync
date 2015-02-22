from unittest2 import TestCase, main
from tests.test_utilities import path_for, TempFile
from sftpsync.sftpsync import ssh_config

class SftpSyncTest(TestCase):

    def test_ssh_config(self):
        config = ssh_config(path_for('test_ssh_config'))
        hostnames = config.get_hostnames()
        self.assertEquals(len(hostnames), 3)
        self.assertEquals(hostnames, set(['*', 'proxy-server', 'sftp-server']))

    def test_ssh_config__proxy_server(self):
        config = ssh_config(path_for('test_ssh_config')).lookup('proxy-server')
        self.assertEquals(len(config), 3)
        self.assertEquals(config['user'],         'foo')
        self.assertEquals(config['hostname'],     'proxy-server.example.com')
        self.assertEquals(config['identityfile'], ['./test_proxy_server_rsa'])

    def test_ssh_config__sftp_server(self):
        config = ssh_config(path_for('test_ssh_config')).lookup('sftp-server')
        self.assertEquals(len(config), 4)
        self.assertEquals(config['user'],         'bar')
        self.assertEquals(config['hostname'],     'sftp-server.example.com')
        self.assertEquals(config['identityfile'], ['./test_sftp_server_rsa'])
        # Proxy settings are automatically infered from the previous 'proxy-server' entry in the file:
        self.assertEquals(config['proxycommand'], 'ssh proxy-server nc sftp-server.example.com 22')

    def test_ssh_config__non_existant_server_entry(self):
        config = ssh_config(path_for('test_ssh_config')).lookup('non-existant-server')
        self.assertEquals(len(config), 1)
        self.assertEquals(config['hostname'], 'non-existant-server')

    def test_ssh_config__non_existant_ssh_config_file(self):
        config = ssh_config(path_for('non-existant-ssh-config-file')).lookup('sftp-server')
        self.assertEquals(len(config), 1)
        self.assertEquals(config['hostname'], 'sftp-server')

    def test_ssh_config__empty_ssh_config_file(self):
        with TempFile() as path:
            config = ssh_config(path).lookup('sftp-server')
            self.assertEquals(len(config), 1)
            self.assertEquals(config['hostname'], 'sftp-server')

if __name__ == '__main__':
    main()
