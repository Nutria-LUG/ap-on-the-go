#!/usr/bin/python


class BashManager:
    _runner = None
    _pipe = None

    def __init__(self):
        from subprocess import Popen, PIPE
        self._runner = Popen
        self._pipe = PIPE

    def run(self, command):
        # print(command)
        process = self._runner(
            command,
            shell=True,
            stdout=self._pipe,
            stderr=self._pipe
        )
        return process.communicate()


class FileManager:
    def create_or_replace_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content)

    def read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def remove_file(self, path):
        import os
        if os.path.exists(path):
            os.remove(path)


class HostAPDManager:
    _configs = {
        'channel': '1',
        'country_code': 'IT',
        'driver': 'nl80211',
        'hw_mode': 'g',
        'ssid': 'MyAccessPoint',
        'wpa': '2',
        'wpa_key_mgmt': 'WPA-PSK',
    }

    def run_wizard(self, interface):
        self._update_configs()
        self._set_password()
        self._set_interface(interface)

    def export_config(self):
        config = ''
        for (key, val) in self._configs.items():
            config += '%s=%s\n' % (key, val)
        return config

    def _update_configs(self):
        for (key, val) in self._configs.items():
            tmp = input('%s: [%s] ' % (key, val))
            self._configs[key] = tmp or val

    def _set_interface(self, interface):
        self._configs['interface'] = interface

    def _validate_password(self, password):
        if len(password) < 8:
            return False
        return True

    def _set_password(self):
        from getpass import getpass
        password = getpass('password: ')
        if not self._validate_password(password):
            self._set_password()
        else:
            self._configs['wpa_passphrase'] = password


class DnsMasqManager:
    _configs = {
        'interface': '',
        'dhcp-range': ''
    }
    _dhcp_configs = {
        'dhcp start ip': '10.0.0.2',
        'dhcp end ip': '10.0.0.5',
        'dhcp subnet': '255.255.255.0',
        'dhcp expire': '12h'
    }

    def run_wizard(self, interface):
        self._set_interface(interface)
        self._update_dhcp_configs()

    def export_config(self):
        config = ''
        for (key, val) in self._configs.items():
            config += '%s=%s\n' % (key, val)
        return config

    def _set_interface(self, interface):
        self._configs['interface'] = interface

    def _update_dhcp_configs(self):
        dhcp_config = ''
        for (key, val) in self._dhcp_configs.items():
            tmp = input('%s: [%s] ' % (key, val))
            dhcp_config += '%s,' % (tmp or val)
        self._configs['dhcp-range'] = dhcp_config[:-1]


class NetworkManager:
    _sh = None

    def __init__(self, sh):
        self._sh = sh

    def start_ap_daemon(self, iface, virtual_iface, ip_addr, dns_conf, apd_conf):
        if not self.exists_iface(virtual_iface):
            mac_address = self.generate_random_macaddress()
            self.create_virtual_iface(iface, virtual_iface, mac_address)
        self.enable_iface(virtual_iface)
        self.set_ip_address(virtual_iface, ip_addr)
        self.run_ap_daemon(dns_conf, apd_conf)

    def stop_ap_daemon(self):
        self.kill_ap_daemon()

    def exists_iface(self, interface):
        bash_command = 'ip link | grep %s' % interface
        (result, error) = self._sh(bash_command)
        return True if result and len(result) > 0 else False

    def enable_iface(self, iface):
        bash_command = 'ip link set %s up' % iface
        self._sh(bash_command)

    def set_ip_address(self, iface, ip_addr):
        bash_command = 'ip addr add %s/24 dev %s' % (ip_addr, iface)
        self._sh(bash_command)

    def enable_ip_forwarding(self, iface):
        bash_command = 'sysctl net.ipv4.conf.%s.forwarding=1' % iface
        self._sh(bash_command)

    def create_virtual_iface(self, iface, virtual_iface, mac_address):
        bash_command = 'iw dev %s interface add %s type managed addr %s' % (
            iface, virtual_iface, mac_address)
        self._sh(bash_command)

    def run_ap_daemon(self, dns_conf, apd_conf):
        bash_dns_command = 'dnsmasq -C %s' % dns_conf
        self._sh(bash_dns_command)
        bash_apd_command = 'hostapd %s' % apd_conf
        self._sh(bash_apd_command)

    def kill_ap_daemon(self):
        bash_dns_command = 'killall dnsmasq'
        self._sh(bash_dns_command)
        bash_apd_command = 'killall hostapd'
        self._sh(bash_apd_command)

    def generate_random_macaddress(self):
        import random
        return ''.join(['%02x:' % random.randint(0, 255) for i in range(6)])[:-1]


class ScriptManager:
    _args = None
    _default_ip = '10.0.0.1'
    _iface_path = 'interface.conf'
    _ipaddr_path = 'ipaddress.conf'
    _hostapd_path = 'hostapd.conf'
    _dnsmasq_path = 'dnsmasq.conf'

    def __init__(self, args):
        self._args = args

    def run_or_show_usage(self):
        if not self._validate_args():
            self._usage()

        action = self._get_action()
        folder = self._get_folder()
        if not hasattr(self, action):
            self._usage()
        else:
            getattr(self, action)(folder)

    def _validate_args(self):
        return len(self._args) in [2, 3]

    def _get_action(self):
        return '_%s' % self._args[1]

    def _get_folder(self):
        return self._args[1] if len(self._args) == 2 else "."

    def _usage(self):
        print('init: generate required config files')
        print('start: start access point mode')
        print('stop: stop access point mode')
        print('purge: stop and remove all config files')
        exit()

    def _generate_virtual_iface_name(self, interface):
        return '%s_ap' % interface

    def _set_interface(self):
        interface = input('interface: ')
        if not self._validate_interface(interface):
            return self._set_interface()
        else:
            return interface

    def _validate_interface(self, interface):
        return True if len(interface) > 2 else False

    def _set_ip_address(self):
        tmp = input('static ip: [%s] ' % self._default_ip)
        if not self._validate_ip_address(tmp):
            return self._set_ip_address()
        else:
            return tmp or self._default_ip

    def _validate_ip_address(self, ip_address):
        return True

    def _init(self, folder):
        print('init')

        iface = self._set_interface()
        ip_addr = self._set_ip_address()
        file_manager = FileManager()
        dns_manager = DnsMasqManager()
        apd_manager = HostAPDManager()
        virtual_iface = self._generate_virtual_iface_name(iface)

        dns_manager.run_wizard(virtual_iface)
        apd_manager.run_wizard(virtual_iface)
        dns_config = dns_manager.export_config()
        apd_config = apd_manager.export_config()

        file_manager.create_or_replace_file(self._iface_path, iface)
        file_manager.create_or_replace_file(self._ipaddr_path, ip_addr)
        file_manager.create_or_replace_file(self._dnsmasq_path, dns_config)
        file_manager.create_or_replace_file(self._hostapd_path, apd_config)

        print('done')

    def _start(self, folder):
        print('start')

        bash_manager = BashManager()
        file_manager = FileManager()
        net_manager = NetworkManager(bash_manager.run)
        iface = file_manager.read_file(self._iface_path)
        ip_addr = file_manager.read_file(self._ipaddr_path)
        virtual_iface = self._generate_virtual_iface_name(iface)
        dns_conf = self._dnsmasq_path
        apd_conf = self._hostapd_path

        net_manager.start_ap_daemon(
            iface, virtual_iface, ip_addr, dns_conf, apd_conf)

        print('done')

    def _stop(self, folder):
        print('stop')

        bash_manager = BashManager()
        net_manager = NetworkManager(bash_manager.run)

        net_manager.stop_ap_daemon()

        print('done')

    def _purge(self, folder):
        print('purge')

        self._stop(folder)

        file_manager = FileManager()

        file_manager.remove_file(self._iface_path)
        file_manager.remove_file(self._ipaddr_path)
        file_manager.remove_file(self._dnsmasq_path)
        file_manager.remove_file(self._hostapd_path)

        print('done')


def main(args):
    script_manager = ScriptManager(args)
    script_manager.run_or_show_usage()


import sys
main(sys.argv)
