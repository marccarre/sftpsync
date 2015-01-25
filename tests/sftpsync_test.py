import os
from socks import SOCKS4, SOCKS5
from tempfile import mktemp
from unittest2 import TestCase, main
from sftpsync import ssh_config, _parse_socks_version

class SftpSyncTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test___parse_socks_version__SOCKS4(self):
        self.assertEquals(SOCKS4, _parse_socks_version('SOCKS4'))

    def test___parse_socks_version__SOCKS5(self):
        self.assertEquals(SOCKS5, _parse_socks_version('SOCKS5'))

    def test___parse_socks_version__invalid_sock_version(self):
        self.assertRaisesRegexp(
            ValueError, 
            'Invalid SOCKS version: "invalid-version". Please choose one of the following values: "SOCKS4", "SOCKS5".', 
            _parse_socks_version, 
            'invalid-version'
        )

    def test_ssh_config__proxy_server(self):
        config = ssh_config('proxy-server', current_dir() + '/test_ssh_config')
        self.assertEquals(3, len(config))
        self.assertEquals('foo',                config['user'])
        self.assertEquals('proxy.example.com',  config['hostname'])
        self.assertEquals(['./test_proxy_rsa'], config['identityfile'])

    def test_ssh_config__destination_server(self):
        config = ssh_config('destination-server', current_dir() + '/test_ssh_config')
        self.assertEquals(4, len(config))
        self.assertEquals('bar',                                     config['user'])
        self.assertEquals('real.example.com',                        config['hostname'])
        self.assertEquals(['./test_real_rsa'],                       config['identityfile'])
        # Proxy settings are automatically infered from the previous 'proxy-server' entry in the file:
        self.assertEquals('ssh proxy-server nc real.example.com 22', config['proxycommand'])

    def test_ssh_config__non_existant_server_entry(self):
        config = ssh_config('non-existant-server', current_dir() + '/test_ssh_config')
        self.assertEquals(1, len(config))
        self.assertEquals('non-existant-server', config['hostname'])

    def test_ssh_config__non_existant_ssh_config_file(self):
        config = ssh_config('non-existant-ssh-config-file', mktemp())
        self.assertEquals(1, len(config))
        self.assertEquals('non-existant-ssh-config-file', config['hostname'])
        



def current_dir():
    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    main()

