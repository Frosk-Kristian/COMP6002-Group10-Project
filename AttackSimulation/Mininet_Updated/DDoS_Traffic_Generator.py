from random import randrange, choice
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime

class CustomNetworkTopo(Topo):
    def build(self):
        switches = {}
        hosts = {}

        for i in range(1, 7):
            switch_id = 's' + str(i)
            switches[switch_id] = self.addSwitch(switch_id, cls=OVSKernelSwitch, protocols='OpenFlow13')
            for j in range(1, 4):
                host_id = (i-1) * 3 + j
                host_name = 'h' + str(host_id)
                hosts[host_name] = self.addHost(
                    host_name,
                    cpu=1.0 / 20,
                    mac="00:00:00:00:00:%02x" % host_id,
                    ip="10.0.0." + str(host_id) + "/24"
                )
                self.addLink(hosts[host_name], switches[switch_id])

        for i in range(1, 6):
            self.addLink(switches['s' + str(i)], switches['s' + str(i+1)])

def generate_random_ip():
    ip_prefix = "10.0.0."
    random_part = str(randrange(1, 19))  # Ensuring the random IP matches host IPs
    return ip_prefix + random_part

def initiate_network():
    info("Starting the network setup...\n")
    topo = CustomNetworkTopo()
    controller_ip = '192.168.56.114'
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController('c0', controller=RemoteController, ip=controller_ip, port=6653)

    net.start()

    hosts = [net.get('h' + str(i + 1)) for i in range(18)]

    h1 = hosts[0]
    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('python -m SimpleHTTPServer 80 &')

    sleep(2)  # Give some time for the HTTP server to start

    def perform_attack(attack_name, cmd):
        src_host = choice(hosts)
        target_ip = generate_random_ip()
        formatted_cmd = cmd.format(target_ip)
        info("Initiating " + attack_name + " from " + src_host.name + " to " + target_ip + "\n")  # Assuming src_host has a .name attribute
        src_host.cmd(cmd.format(target_ip))
        sleep(2)  # Allow time for the attack to be carried out
        info("Completed " + attack_name + " from " + src_host.name + " to " + target_ip + "\n")

    attack_commands = {
        "ICMP (Ping) Flood": "timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --flood {}",
        "UDP Flood": "timeout 20s hping3 -2 -V -d 120 -w 64 --flood {}",
        "TCP-SYN Flood": "timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --flood {}"
    }

    for attack_name, command in attack_commands.items():
        perform_attack(attack_name, command)
        sleep(2)

    net.stop()
    info("Network shutdown complete.\n")

if __name__ == '__main__':
    start_time = datetime.now()
    setLogLevel('info')
    initiate_network()
    end_time = datetime.now()
    total_runtime = end_time - start_time
    info("Total network run time: " + str(total_runtime) + "\n")
