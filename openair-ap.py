#!/usr/bin/python

import sys
from subprocess import Popen, PIPE

_VIRTUAL_IFACE_ = "ap0"
_IFACE = "wlan0"
_DNSMASQ_CONF_ = "/etc/openair-dnsmasq.conf"
_HOSTAPD_CONF_ = "/etc/openair-hostapd.conf"

class BashManager:
    _runner = None
    _pipe = None

    def __init__(self):
        self._runner = Popen
        self._pipe = PIPE

    def run(self, command):
        process = self._runner(
            command,
            shell=True,
            stdout=self._pipe,
            stderr=self._pipe
        )
        return process.communicate()

def _exists_iface(bash_manager, interface):
    bash_command = 'ip link | grep %s' % interface
    (result, error) = bash_manager.run(bash_command)
    return result and len(result) > 0

def _create_virtual_iface(bash_manager, iface, virtual_iface):
    bash_command = "brctl addbr %s" % (virtual_iface)
    bash_manager.run(bash_command)
    bash_command = "iw dev %s set addr4 on" %s (iface)
    bash_manager.run(bash_command)
    bash_command = "brctl addif %s %s" %s (virtual_iface, iface)
    bash_manager.run(bash_command)

def _enable_iface(bash_manager, iface):
    bash_command = "ip link set %s up" % (iface)
    bash_manager.run(bash_command)

def _run_ap_daemon(bash_manager, dns_conf, apd_conf):
    bash_command = "dnsmasq -C %s" % dns_conf
    bash_manager.run(bash_command)
    bash_command = "hostapd -C %s" % apd_conf
    bash_manager.run(bash_command)

def _stop_ap_daemon(bash_manager, virtual_iface):
    bash_command = "ip link set %s down" % (virtual_iface)
    bash_manager.run(bash_command)
    if _exists_interface(bash_manager, virtual_iface):
        bash_command = "brctl delbr %s" % (iface)
        bash_manager.run(bash_command)
    bash_command = "killall dnsmasq"
    bash_manager.run(bash_command)
    bash_command = "killall hostapd"
    bash_manager.run(bash_command)

def start_ap(bash_manager):
    if not _exists_iface(bash_manager, _VIRTUAL_IFACE_):
        _create_virtual_iface(bash_manager, _IFACE_, _VIRTUAL_IFACE_)
    _enable_iface(bash_manager, _VIRTUAL_IFACE_)
    _run_ap_daemon(bash_manager, _DNSMASQ_CONF_, _HOSTAPD_CONF_)

def stop_ap(bash_manager):
    _stop_ap_daemon(bash_manager, _VIRTUAL_IFACE_)

def print_usage():
    print("Usage: ")
    print(" openair-ap start|stop")

if __name__ == "__main__":
    bash_manager = BashManager()
    if len(sys.argv) < 2:
        print_usage()
    elif sys.argv[1] == "start":
        start_ap(bash_manager)
    elif sys.argv[1] == "stop":
        stop_ap(bash_manager)
    else:
        print_usage()
