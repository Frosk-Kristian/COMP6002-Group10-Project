import My_Switch
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from datetime import datetime
import numpy as np

class TrainingStatsCollector(My_Switch.AdvancedSwitch):
    def __init__(self, *args, **kwargs):
        super(TrainingStatsCollector, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.flow_data = {}

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.info('Registered datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.info('Unregistered datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.info('Sending stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        timestamp = datetime.now().timestamp()
        file = open("DATASet.csv", "a+")

        body = ev.msg.body
        for stat in sorted([flow for flow in body if flow.priority == 1], key=lambda flow: (
                flow.match.get('eth_type', 0), flow.match.get('ipv4_src', ''), flow.match.get('ipv4_dst', ''), flow.match.get('ip_proto', 0))):
            
            ip_src = stat.match.get('ipv4_src', '0.0.0.0')
            ip_dst = stat.match.get('ipv4_dst', '0.0.0.0')
            ip_proto = stat.match.get('ip_proto', 0)
            icmp_code = stat.match.get('icmpv4_code', -1)
            icmp_type = stat.match.get('icmpv4_type', -1)
            tp_src = stat.match.get('tcp_src', stat.match.get('udp_src', 0))
            tp_dst = stat.match.get('tcp_dst', stat.match.get('udp_dst', 0))

            flow_id = f"{ip_src}-{tp_src}-{ip_dst}-{tp_dst}-{ip_proto}"

            if flow_id not in self.flow_data:
                self.flow_data[flow_id] = {
                    'timestamps': [],
                    'packet_counts': [],
                    'byte_counts': [],
                    'forward_packets': [],
                    'backward_packets': [],
                    'forward_bytes': [],
                    'backward_bytes': [],
                }

            self.flow_data[flow_id]['timestamps'].append(stat.duration_sec + stat.duration_nsec / 1e9)
            self.flow_data[flow_id]['packet_counts'].append(stat.packet_count)
            self.flow_data[flow_id]['byte_counts'].append(stat.byte_count)

            # Using numpy for statistical calculations
            total_fwd_packets = np.sum(self.flow_data[flow_id]['forward_packets'])
            total_bwd_packets = np.sum(self.flow_data[flow_id]['backward_packets'])
            total_length_fwd_packets = np.sum(self.flow_data[flow_id]['forward_bytes'])
            total_length_bwd_packets = np.sum(self.flow_data[flow_id]['backward_bytes'])
            fwd_packet_length_max = np.max(self.flow_data[flow_id]['forward_bytes']) if self.flow_data[flow_id]['forward_bytes'] else 0
            fwd_packet_length_min = np.min(self.flow_data[flow_id]['forward_bytes']) if self.flow_data[flow_id]['forward_bytes'] else 0
            fwd_packet_length_mean = np.mean(self.flow_data[flow_id]['forward_bytes']) if self.flow_data[flow_id]['forward_bytes'] else 0
            fwd_packet_length_std = np.std(self.flow_data[flow_id]['forward_bytes']) if self.flow_data[flow_id]['forward_bytes'] else 0
            bwd_packet_length_max = np.max(self.flow_data[flow_id]['backward_bytes']) if self.flow_data[flow_id]['backward_bytes'] else 0
            bwd_packet_length_min = np.min(self.flow_data[flow_id]['backward_bytes']) if self.flow_data[flow_id]['backward_bytes'] else 0
            bwd_packet_length_mean = np.mean(self.flow_data[flow_id]['backward_bytes']) if self.flow_data[flow_id]['backward_bytes'] else 0
            bwd_packet_length_std = np.std(self.flow_data[flow_id]['backward_bytes']) if self.flow_data[flow_id]['backward_bytes'] else 0
            max_packet_length = np.max(self.flow_data[flow_id]['byte_counts'])
            min_packet_length = np.min(self.flow_data[flow_id]['byte_counts'])
            packet_length_mean = np.mean(self.flow_data[flow_id]['byte_counts'])
            packet_length_std = np.std(self.flow_data[flow_id]['byte_counts'])
            packet_length_variance = np.var(self.flow_data[flow_id]['byte_counts'])
            fwd_header_length = stat.match.get('tcp_hdr_length', stat.match.get('udp_hdr_length', 0))
            bwd_header_length = 0  # Placeholder for backward header length (need actual extraction logic)
            min_seg_size_fwd = 0  # Placeholder for minimum segment size forward (need actual extraction logic)
            act_data_pkt_fwd = len(self.flow_data[flow_id]['forward_packets'])
            flow_iat = np.diff(self.flow_data[flow_id]['timestamps'])
            flow_iat_mean = np.mean(flow_iat) if flow_iat.size > 0 else 0
            flow_iat_max = np.max(flow_iat) if flow_iat.size > 0 else 0
            flow_iat_min = np.min(flow_iat) if flow_iat.size > 0 else 0
            flow_iat_std = np.std(flow_iat) if flow_iat.size > 0 else 0
            fwd_iat_total = np.sum(flow_iat) if flow_iat.size > 0 else 0
            fwd_iat_max = np.max(flow_iat) if flow_iat.size > 0 else 0
            fwd_iat_min = np.min(flow_iat) if flow_iat.size > 0 else 0
            fwd_iat_mean = np.mean(flow_iat) if flow_iat.size > 0 else 0
            fwd_iat_std = np.std(flow_iat) if flow_iat.size > 0 else 0
            bwd_iat_total = 0  # Placeholder for total backward inter-arrival time (need actual extraction logic)
            bwd_iat_max = 0  # Placeholder for max backward inter-arrival time (need actual extraction logic)
            bwd_iat_min = 0  # Placeholder for min backward inter-arrival time (need actual extraction logic)
            bwd_iat_mean = 0  # Placeholder for mean backward inter-arrival time (need actual extraction logic)
            bwd_iat_std = 0  # Placeholder for std deviation of backward inter-arrival time (need actual extraction logic)
            fwd_psh_flags = stat.match.get('tcp_flags', 0) & 0x08
            bwd_psh_flags = 0  # Placeholder for backward PSH flags (need actual extraction logic)
            fwd_urg_flags = stat.match.get('tcp_flags', 0) & 0x20
            bwd_urg_flags = 0  # Placeholder for backward URG flags (need actual extraction logic)
            fin_flag_count = stat.match.get('tcp_flags', 0) & 0x01
            syn_flag_count = stat.match.get('tcp_flags', 0) & 0x02
            rst_flag_count = stat.match.get('tcp_flags', 0) & 0x04
            psh_flag_count = stat.match.get('tcp_flags', 0) & 0x08
            ack_flag_count = stat.match.get('tcp_flags', 0) & 0x10
            urg_flag_count = stat.match.get('tcp_flags', 0) & 0x20
            ece_flag_count = stat.match.get('tcp_flags', 0) & 0x40
            down_up_ratio = total_fwd_packets / total_bwd_packets if total_bwd_packets > 0 else 0
            avg_packet_size = np.mean(self.flow_data[flow_id]['byte_counts']) if self.flow_data[flow_id]['byte_counts'] else 0
            init_win_bytes_fwd = 0  # Placeholder for initial window bytes forward (need actual extraction logic)
            init_win_bytes_bwd = 0  # Placeholder for initial window bytes backward (need actual extraction logic)
            active_max = 0  # Placeholder for max active time (need actual extraction logic)
            active_min = 0  # Placeholder for min active time (need actual extraction logic)
            active_mean = 0  # Placeholder for mean active time (need actual extraction logic)
            active_std = 0  # Placeholder for std deviation of active time (need actual extraction logic)
            idle_max = 0  # Placeholder for max idle time (need actual extraction logic)
            idle_min = 0  # Placeholder for min idle time (need actual extraction logic)
            idle_mean = 0  # Placeholder for mean idle time (need actual extraction logic)
            idle_std = 0  # Placeholder for std deviation of idle time (need actual extraction logic)
            packet_count_per_second = 0  # Placeholder for Packet Count
            packet_count_per_nsecond = 0  # Placeholder for Packet Count
            byte_count_per_second = 0  # Placeholder for Packet Count
            byte_count_per_nsecond = 0  # Placeholder for Packet Count
            fwd_avg_bytes_bulk = 0  # Placeholder for average bytes in forward bulk (need actual extraction logic)
            fwd_avg_packets_bulk = 0  # Placeholder for average packets in forward bulk (need actual extraction logic)
            bwd_avg_bulk_rate = 0  # Placeholder for average bulk rate in backward direction (need actual extraction logic)
            bwd_avg_packets_bulk = 0  # Placeholder for average packets in backward bulk (need actual extraction logic)
            fwd_avg_bulk_rate = 0  # Placeholder for average bulk rate in forward direction (need actual extraction logic)
            bwd_avg_bytes_bulk = 0  # Placeholder for average bytes in backward bulk (need actual extraction logic)
            avg_fwd_segment_size = np.mean(self.flow_data[flow_id]['forward_bytes']) if self.flow_data[flow_id]['forward_bytes'] else 0
            avg_bwd_segment_size = np.mean(self.flow_data[flow_id]['backward_bytes']) if self.flow_data[flow_id]['backward_bytes'] else 0
            cwe_flag_count = 0  # Placeholder for CWE flag count (need actual extraction logic)
            subflow_fwd_packets = total_fwd_packets
            subflow_bwd_packets = total_bwd_packets
            subflow_fwd_bytes = total_length_fwd_packets
            subflow_bwd_bytes = total_length_bwd_packets
            label = "DDoS"

            # Writing data to CSV
            file.write(f"{timestamp},{ev.msg.datapath.id},{flow_id},{ip_src},{tp_src},{ip_dst},{tp_dst},{ip_proto},"
                       f"{icmp_code},{icmp_type},{stat.duration_sec},{stat.duration_nsec},{stat.idle_timeout},"
                       f"{stat.hard_timeout},{stat.flags},{stat.packet_count},{stat.byte_count},"
                       f"{packet_count_per_second},{packet_count_per_nsecond},{byte_count_per_second},{byte_count_per_nsecond},"
                       f"{total_fwd_packets},{total_bwd_packets},{total_length_fwd_packets},{total_length_bwd_packets},"
                       f"{fwd_packet_length_max},{fwd_packet_length_min},{fwd_packet_length_mean},{fwd_packet_length_std},"
                       f"{bwd_packet_length_max},{bwd_packet_length_min},{bwd_packet_length_mean},{bwd_packet_length_std},"
                       f"{max_packet_length},{min_packet_length},{packet_length_mean},{packet_length_std},{packet_length_variance},"
                       f"{fwd_header_length},{bwd_header_length},{min_seg_size_fwd},{act_data_pkt_fwd},"
                       f"{flow_iat_mean},{flow_iat_max},{flow_iat_min},{flow_iat_std},"
                       f"{fwd_iat_total},{fwd_iat_max},{fwd_iat_min},{fwd_iat_mean},{fwd_iat_std},"
                       f"{bwd_iat_total},{bwd_iat_max},{bwd_iat_min},{bwd_iat_mean},{bwd_iat_std},"
                       f"{fwd_psh_flags},{bwd_psh_flags},{fwd_urg_flags},{bwd_urg_flags},"
                       f"{fin_flag_count},{syn_flag_count},{rst_flag_count},{psh_flag_count},"
                       f"{ack_flag_count},{urg_flag_count},{ece_flag_count},{down_up_ratio},{avg_packet_size},"
                       f"{init_win_bytes_fwd},{init_win_bytes_bwd},{active_max},{active_min},{active_mean},{active_std},"
                       f"{idle_max},{idle_min},{idle_mean},{idle_std},{fwd_avg_bytes_bulk},{fwd_avg_packets_bulk},{bwd_avg_bulk_rate},"
                       f"{bwd_avg_packets_bulk},{fwd_avg_bulk_rate},{bwd_avg_bytes_bulk},{avg_fwd_segment_size},{avg_bwd_segment_size},"
                       f"{cwe_flag_count},{subflow_fwd_packets},{subflow_bwd_packets},{subflow_fwd_bytes},{subflow_bwd_bytes},{label}\n")

        file.close()

if __name__ == '__main__':
    from ryu.cmd.manager import main
    main()
