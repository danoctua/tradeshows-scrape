from pathlib import Path

from exhibitions.utils.exceptions import SecretDoesntExistException

# Path where secrets have to be stored.
# Put all files with your secrets there.
SECRETS_PATH = "files"


def get_secret(name: str) -> str:
    """Function to get secrets from all places it could be located

    :param name: secret name for lookup
    :return: found secret
    :raises SecretDoesntExistException: no secret with passed name found
    """
    secret_path = Path(SECRETS_PATH) / name
    if not secret_path.exists():
        raise SecretDoesntExistException(f"No secret with the name {name}")

    with open(secret_path, "r") as file:
        data = file.read()

    return data
