from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

# Global variable for flow serial number
FLOW_COUNTER = 0

def increment_flow_number():
    global FLOW_COUNTER
    FLOW_COUNTER += 1
    return FLOW_COUNTER

class AdvancedSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AdvancedSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port_mapping = {}
        self.arp_ip_to_port_mapping = {}
        self.mitigation_enabled = False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def on_switch_features(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        flow_id = increment_flow_number()
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, 0, match, actions, flow_id)

    def _add_flow(self, datapath, priority, match, actions, flow_id, buffer_id=None, idle_timeout=0, hard_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            flow_mod = parser.OFPFlowMod(datapath=datapath, cookie=flow_id, buffer_id=buffer_id,
                                         idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                                         priority=priority, match=match, instructions=instructions)
        else:
            flow_mod = parser.OFPFlowMod(datapath=datapath, cookie=flow_id, priority=priority,
                                         idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                                         match=match, instructions=instructions)
        datapath.send_msg(flow_mod)

    def block_incoming_port(self, datapath, port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=port)
        actions = []
        flow_id = increment_flow_number()
        self._add_flow(datapath, 100, match, actions, flow_id, hard_timeout=120)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def handle_packet_in(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore LLDP packets
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dpid = datapath.id
        self.mac_to_port_mapping.setdefault(dpid, {})
        self.arp_ip_to_port_mapping.setdefault(dpid, {})
        self.arp_ip_to_port_mapping[dpid].setdefault(in_port, [])

        src_mac = eth.src
        dst_mac = eth.dst

        # Learn the source MAC to port mapping
        self.mac_to_port_mapping[dpid][src_mac] = in_port

        # Determine the output port
        if dst_mac in self.mac_to_port_mapping[dpid]:
            out_port = self.mac_to_port_mapping[dpid][dst_mac]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Process ARP packets
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            arp_pkt = pkt.get_protocol(arp.arp)
            if arp_pkt.opcode == arp.ARP_REQUEST or arp.ARP_REPLY:
                if arp_pkt.src_ip not in self.arp_ip_to_port_mapping[dpid][in_port]:
                    self.arp_ip_to_port_mapping[dpid][in_port].append(arp_pkt.src_ip)

        # Avoid packet_in next time by installing a flow rule
        if out_port != ofproto.OFPP_FLOOD:
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip_pkt = pkt.get_protocol(ipv4.ipv4)
                src_ip = ip_pkt.src
                dst_ip = ip_pkt.dst
                protocol = ip_pkt.proto

                if protocol == in_proto.IPPROTO_ICMP:
                    icmp_pkt = pkt.get_protocol(icmp.icmp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                            ipv4_src=src_ip, ipv4_dst=dst_ip,
                                            ip_proto=protocol,
                                            icmpv4_code=icmp_pkt.code,
                                            icmpv4_type=icmp_pkt.type)
                elif protocol == in_proto.IPPROTO_TCP:
                    tcp_pkt = pkt.get_protocol(tcp.tcp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                            ipv4_src=src_ip, ipv4_dst=dst_ip,
                                            ip_proto=protocol,
                                            tcp_src=tcp_pkt.src_port, tcp_dst=tcp_pkt.dst_port)
                elif protocol == in_proto.IPPROTO_UDP:
                    udp_pkt = pkt.get_protocol(udp.udp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                            ipv4_src=src_ip, ipv4_dst=dst_ip,
                                            ip_proto=protocol,
                                            udp_src=udp_pkt.src_port, udp_dst=udp_pkt.dst_port)

                if self.mitigation_enabled:
                    if src_ip not in self.arp_ip_to_port_mapping[dpid][in_port]:
                        self.logger.info(f"Potential attack detected from port {in_port}. Blocking the port.")
                        self.block_incoming_port(datapath, in_port)
                        return

                flow_id = increment_flow_number()
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self._add_flow(datapath, 1, match, actions, flow_id, msg.buffer_id, idle_timeout=20, hard_timeout=100)
                    return
                else:
                    self._add_flow(datapath, 1, match, actions, flow_id, idle_timeout=20, hard_timeout=100)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        packet_out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                         in_port=in_port, actions=actions, data=data)
        datapath.send_msg(packet_out)
