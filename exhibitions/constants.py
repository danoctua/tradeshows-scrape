from exhibitions.utils.secrets import get_secret

# Crawls-related constants

# Update this constant with your initials before making the crawl
SUBMITTED_BY = "DM"

# Proxies

# Store your proxy configuration here.
# For password-based authentication - set host, port, username and password attributes.
# For token-based authentication - set host, port and token attributes
PROXY_ZYTE = "ProxyZyte"
PROXY_BRIGHT_DATA = "ProxyBrightData"

DEFAULT_PROXY = PROXY_ZYTE

PROXY_CONFIGURATION = {
    PROXY_ZYTE: {
        "token": get_secret("ZYTE_SP"),
        "host": get_secret("ZYTE_HOST"),
        "port": 8010,
    },
    PROXY_BRIGHT_DATA: {
        "username": get_secret("BRIGHT_DATA_USER"),
        "password": get_secret("BRIGHT_DATA_PASSWORD"),
        "host": get_secret("BRIGHT_DATA_HOST"),
        "port": 22225,
    },
}
