#!/bin/sh

IPTABLES_COMMENT="redirect-udp-hysteria"
RULE_SPEC="-p udp -m multiport --dport 443,10000:50000 -j REDIRECT --to-ports 1935"
if ! iptables -t nat -C PREROUTING -m comment --comment "$IPTABLES_COMMENT" $RULE_SPEC 2>/dev/null; then
    LINE=$(iptables -t nat -L PREROUTING --line-numbers -n 2>/dev/null | awk -v comment="$IPTABLES_COMMENT" 'index($0, comment){print $1;exit}')
    [ -z "$LINE" ] || iptables -t nat -D PREROUTING "$LINE"
    iptables -t nat -A PREROUTING -m comment --comment "$IPTABLES_COMMENT" $RULE_SPEC
fi

#modprobe tcp_bbr
# sysctl -w net.ipv4.ip_unprivileged_port_start=443
sysctl -w fs.file-max=1048576  # max open files for 1Gb
sysctl -w net.core.rmem_max=16777216  # max read buffer  16777216 (16Gb)
sysctl -w net.core.wmem_max=16777216  # max write buffer  16777216 (16Gb)
sysctl -w net.core.rmem_default=212992  # default read buffer
sysctl -w net.core.wmem_default=212992  # default write buffer
sysctl -w net.core.netdev_max_backlog=4096  # max processor input queue
sysctl -w net.core.somaxconn=4096  # max backlog
sysctl -w net.ipv4.tcp_syncookies=1  # resist SYN flood attacks
sysctl -w net.ipv4.tcp_tw_reuse=1  # reuse timewait sockets when safe
# sysctl -w net.ipv4.tcp_tw_recycle="0"  # turn off fast timewait sockets recycling
sysctl -w net.ipv4.tcp_slow_start_after_idle=0
sysctl -w net.ipv4.tcp_fin_timeout=30  # short FIN timeout
sysctl -w net.ipv4.tcp_keepalive_time=1200  # short keepalive time
sysctl -w net.ipv4.ip_local_port_range="10000 65000"  # outbound port range
sysctl -w net.ipv4.tcp_max_syn_backlog=4096  # max SYN backlog
sysctl -w net.ipv4.tcp_max_tw_buckets=65536  # max timewait sockets held by system simultaneously
sysctl -w net.ipv4.tcp_fastopen=3  # turn on TCP Fast Open on both client and server side
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"  # TCP receive buffer
sysctl -w net.ipv4.tcp_wmem="4096 87380 16777216"  # TCP write buffer
sysctl -w net.ipv4.tcp_mtu_probing=1  # turn on path MTU discovery
sysctl -w net.core.default_qdisc=fq  # Required for bbr
sysctl -w net.ipv4.tcp_congestion_control=bbr
sysctl -w net.ipv4.tcp_no_metrics_save=1
sysctl -w vm.swappiness=10
