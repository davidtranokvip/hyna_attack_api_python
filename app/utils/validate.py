from app.configs.blacklist import BLACKLISTED_DOMAINS
from urllib.parse import urlparse
from flask import request
from app.configs.whitelist import WHITELISTED_IPS

def is_whitelisted():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    
    return client_ip in WHITELISTED_IPS

def is_blacklisted(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().lstrip("www.")
    return domain in BLACKLISTED_DOMAINS
