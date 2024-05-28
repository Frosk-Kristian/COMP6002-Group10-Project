from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime
from random import randrange, choice

class CustomTopo(Topo):
    def build(self):
        # Adding switches
        switches = []
        for i in range(1, 7):
            switch = self.addSwitch('s{}'.format(i), cls=OVSKernelSwitch, protocols='OpenFlow13')
            switches.append(switch)

        # Adding hosts and connecting them to switches
        for i in range(6):
            for j in range(3):
                host_id = i * 3 + j + 1
                host = self.addHost('h{}'.format(host_id), cpu=1.0 / 20,
                                    mac = "00:00:00:00:00:{:02x}".format(host_id),
                                    ip = "10.0.0.{}/24".format(host_id))
                self.addLink(host, switches[i])

        # Interconnecting switches in a linear topology
        for i in range(len(switches) - 1):
            self.addLink(switches[i], switches[i + 1])

def generate_random_ip():
    # Function to generate a random IP from the defined range
    return "10.0.0.{}".format(randrange(1, 19))

def start_network():
    info("Setting up the network...\n")
    topo = CustomTopo()
    controller_ip = '192.168.56.114'
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController('c0', controller=RemoteController, ip=controller_ip, port=6653)

    net.start()

    hosts = [net.getNodeByName('h{}'.format(i+1)) for i in range(18)]
    
    # Setup web server and iperf on h1
    h1 = hosts[0]
    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('python -m SimpleHTTPServer 80 &')
    h1.cmd('iperf -s -p 5050 &')
    h1.cmd('iperf -s -u -p 5051 &')
    sleep(2)
    
    for host in hosts:
        host.cmd('cd /home/mininet/Downloads')

    for iteration in range(600):
        print("Iteration {}/600\n".format(iteration + 1))
        
        for _ in range(10):
            src = choice(hosts)
            dst_ip = generate_random_ip()
            dst_host_num = dst_ip.split('.')[-1]

            info("Generating ICMP traffic between {} and h{}\n".format(src, dst_host_num))
            info("Generating TCP/UDP traffic between {} and h1\n".format(src))
            
            src.cmd("ping {} -c 100 &".format(dst_ip))
            src.cmd("iperf -p 5050 -c 10.0.0.1")
            src.cmd("iperf -p 5051 -u -c 10.0.0.1")
            
            info("{} downloading index.html from h1\n".format(src))
            src.cmd("wget http://10.0.0.1/index.html")
            info("{} downloading test.zip from h1\n".format(src))
            src.cmd("wget http://10.0.0.1/test.zip")


        h1.cmd("rm -f *.* /home/mininet/Downloads")

    net.stop()
    info("Network stopped.\n")

if __name__ == '__main__':
    start_time = datetime.now()
    
    setLogLevel('info')
    start_network()
    
    end_time = datetime.now()
    info("Total execution time: {}\n".format(end_time - start_time))