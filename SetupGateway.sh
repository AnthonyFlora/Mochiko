
# Run as: 'sudo nohup ./SetupGateway.sh &'
# Goal: 
#  wlan0 provides configuration AP
#  wlan1 connects to external WIFI source
#  eth0 provides 

echo '\n*** INSTALLING PACKAGES ***'
sudo apt-get update
echo 'y' | sudo apt-get upgrade
echo 'y' | sudo apt-get install dnsmasq hostapd
echo 'y' | sudo apt-get install vim

echo '\n*** STOPPING SERVICES ***'
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd

echo '\n*** UPDATING CONFIG dhcpcd.conf ***'
sudo bash -c 'echo "interface wlan0" >> /etc/dhcpcd.conf'
sudo bash -c 'echo "  static ip_address=192.168.20.1/24" >> /etc/dhcpcd.conf'
sudo bash -c 'echo "  static routers=192.168.20.0" >> /etc/dhcpcd.conf'

echo '\n*** STARTING SERVICES ***'
sudo service dhcpcd restart

echo '\n*** UPDATING CONFIG dnsmasq.conf ***'
sudo bash -c 'echo "" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "interface=wlan0" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  listen-address=192.168.20.1" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  bind-interfaces" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  server=8.8.8.8" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  domain-needed" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  bogus-priv" >> /etc/dnsmasq.conf'
sudo bash -c 'echo "  dhcp-range=192.168.20.2,192.168.20.30,255.255.255.0,24h" >> /etc/dnsmasq.conf'

echo '\n*** UPDATING CONFIG hostapd.conf ***'
sudo bash -c 'echo "" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "interface=wlan0" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "hw_mode=g" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "channel=7" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "wmm_enabled=0" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "macaddr_acl=0" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "auth_algs=1" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "ignore_broadcast_ssid=0" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "wpa=2" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "wpa_key_mgmt=WPA-PSK" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "wpa_pairwise=TKIP" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "rsn_pairwise=CCMP" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "ssid=pi-gateway" >> /etc/hostapd/hostapd.conf'
sudo bash -c 'echo "wpa_passphrase=computer" >> /etc/hostapd/hostapd.conf'

echo '\n*** UPDATING CONFIG hostapd ***'
sudo bash -c 'echo "" >> /etc/default/hostapd'
sudo bash -c 'echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" >> /etc/default/hostapd'

echo '\n*** SETTING UP FORWARDING ***'
sudo bash -c 'echo "" >> /etc/sysctl.conf'
sudo bash -c 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf'
sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
sudo iptables -A FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o wlan1 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo sed -i "\$i iptables-restore < /etc/iptables.ipv4.nat" /etc/rc.local


echo '\n*** REBOOTING ***'
sudo reboot
