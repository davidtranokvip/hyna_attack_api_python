from app.configs.blacklist import BLACKLISTED_DOMAINS
from urllib.parse import urlparse

def is_blacklisted(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().replace("www.", "")
    return domain in BLACKLISTED_DOMAINS

