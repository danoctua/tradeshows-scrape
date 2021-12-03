from functools import wraps
import warnings

from scrapy.http import TextResponse


def json_response_wrapper(method):
    @wraps(method)
    def inner(*args, **kwargs):
        """Decorator to convert string script to the python dict from the 'item_script' kwarg

        :raises DocumentStructureError
        """
        warnings.warn(
            "Deprecated: Use TextResponse.json() package method instead.",
            category=DeprecationWarning,
        )
        response: TextResponse = kwargs.get("response") or args[1]
        kwargs["response_json"] = response.json()
        return method(*args, **kwargs)

    return inner
