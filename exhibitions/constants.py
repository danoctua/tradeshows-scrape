from exhibitions.utils.secrets import get_secret


SUBMITTED_BY = "DM"

# Proxies

# Store your proxy configuration here.
# For password-based authentication - set host, port, username and password attributes.
# For token-based authentication - set host, port and token attributes
PROXY_ZYTE = {
    "token": get_secret("ZYTE_SP"),
    "host": get_secret("ZYTE_HOST"),
    "port": 8010,
}
