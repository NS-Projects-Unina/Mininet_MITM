from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel

def arcadeNetwork():
    net = Mininet(controller=OVSController)
    
    net.addController('c0')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    s1 = net.addSwitch('s1')

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    net.start()
    
    # 1. Abilita l'IP forwarding per instradare il traffico intercettato ed evita che il SO di h3 legga i pacchetti non destinati a lui e li cestini (essenziale per MITM)
    h3.cmd("sysctl -w net.ipv4.ip_forward=1")
    
    # 2. Mapping di arcade.shop su 10.0.0.1
    h2.cmd('echo "10.0.0.1 arcade.shop" >> /etc/hosts')
    
    # 3. Apertura terminali
    h1.cmd('xterm &')
    h2.cmd('xterm &')
    h3.cmd('xterm &')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    arcadeNetwork()
