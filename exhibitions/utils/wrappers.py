import json
from functools import wraps

from exhibitions.utils.exceptions import JsonParsingException


def json_response_wrapper(method):
    @wraps(method)
    def inner(*args, **kwargs):
        """Decorator to convert string script to the python dict from the 'item_script' kwarg

        :raises DocumentStructureError
        """
        response = kwargs.get("response") or args[1]
        try:
            response_json = json.loads(response.text)
        except json.JSONDecodeError:
            raise JsonParsingException("Can't parse json from API: ", response.text)
        else:
            kwargs["response_json"] = response_json
        return method(*args, **kwargs)

    return inner
