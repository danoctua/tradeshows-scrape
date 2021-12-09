import base64
import logging

import requests
from scrapy import Request

from exhibitions.constants import DEFAULT_PROXY, PROXY_ZYTE, PROXY_CONFIGURATION

logger = logging.getLogger(__name__)

REQUEST_META_SESSION_KEY = "REQUEST-SESSION"
SESSION_HEADER = "X-Crawlera-Session"


def set_token_authenticated_proxy(request, proxy_info: dict):
    """Prepare proxy credentials and proxy url for token-based proxy

    :param request: scrapy request / splash request
    :param proxy_info: proxy configuration defined in config
    """
    proxy_auth = f"{proxy_info['token']}:"
    proxy_url = f"{proxy_info['host']}:{proxy_info['port']}"
    set_request_proxy_meta(request, proxy_url, proxy_auth)


def set_authenticated_proxy(request, proxy_info: dict):
    """Prepare proxy credentials and proxy url for username-based proxy

    :param request: scrapy request / splash request
    :param proxy_info: proxy configuration defined in config
    """
    proxy_auth = f"{proxy_info['username']}:{proxy_info['password']}"
    proxy_url = f"{proxy_info['host']}:{proxy_info['port']}"
    set_request_proxy_meta(request, proxy_url, proxy_auth)


def set_request_proxy_meta(request, proxy_url: str, proxy_auth: str):
    """Set request meta to use proxy

    :param request: scrapy request / splash request
    :param proxy_url: proxy url as a pair of HOST:PORT
    :param proxy_auth: proxy credentials as the pair of username:password or API token
    """
    proxy_auth_encoded = (
        proxy_auth.encode("utf-8") if not isinstance(proxy_auth, bytes) else proxy_auth
    )
    proxy_authorization_header = b"Basic " + base64.urlsafe_b64encode(
        proxy_auth_encoded
    )
    request.meta["proxy"] = f"http://{proxy_url}"
    request.headers["Proxy-Authorization"] = proxy_authorization_header


def set_zyte_proxy(request, proxy_info: dict):
    """Set default Zyte header for proxy."""
    request.headers.setdefault("X-Crawlera-Profile", "desktop")
    request.headers.setdefault("X-Crawlera-Cookies", "disable")
    set_token_authenticated_proxy(request, proxy_info)


def set_proxy_for_configuration(request: Request, proxy_configuration: dict) -> None:
    if "username" in proxy_configuration and "password" in proxy_configuration:
        set_authenticated_proxy(request, proxy_configuration)
    elif "token" in proxy_configuration:
        set_token_authenticated_proxy(request, proxy_configuration)
    else:
        logger.error("No proper proxy configuration provided")


def set_proxy(request: Request, proxy_name: str) -> None:
    """Set proxy for the request by proxy name"""
    proxy_configuration = PROXY_CONFIGURATION.get(proxy_name)
    if not proxy_configuration:
        proxy_configuration = PROXY_CONFIGURATION.get(DEFAULT_PROXY)
    # Get the proxy set method and set the proxy using it based on the configuration
    set_proxy_method = proxy_method_configuration.get(proxy_name, set_proxy_for_configuration)
    set_proxy_method(request, proxy_configuration)


def get_zyte_session(request: Request, proxy_configuration: dict) -> None:
    """Method to set Zyte session header for the request"""
    if REQUEST_META_SESSION_KEY not in request.meta:
        session_request = requests.post(
            url=f"http://{proxy_configuration['host']}:{proxy_configuration['port']}/sessions",
            auth=(proxy_configuration["token"], "")
        )
        session_key = session_request.text
        request.meta[REQUEST_META_SESSION_KEY] = session_key

    request.headers[SESSION_HEADER] = request.meta[REQUEST_META_SESSION_KEY]


proxy_method_configuration = {
    PROXY_ZYTE: set_zyte_proxy
}
