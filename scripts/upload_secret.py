import argparse
import json
from typing import cast

import google.auth
from google.api_core.exceptions import AlreadyExists
from google.auth.transport.requests import AuthorizedSession

from mlbstandings import light_google_wrappers


PROJECT_ID = "mlb-standings-001"
SECRET_ID = "creds"


def main():
    parser = argparse.ArgumentParser(
        description="Upload local client_secret.json to Secret Manager."
    )
    _ = parser.add_argument(
        "--file_path",
        default="client_secret.json",
        help="Path to your local client_secret.json",
    )

    args = parser.parse_args()
    file_path = cast(str, args.file_path)
    with open(file_path, "r") as f:
        local_json = json.load(f)  # pyright: ignore[reportAny]
    if "installed" not in local_json:
        msg = "Error: ${file_path} file missing 'installed' key."
        raise RuntimeError(msg)
    secrets = light_google_wrappers.Secrets(
        AuthorizedSession(google.auth.default()[0]),  # pyright:ignore[reportUnknownMemberType,reportUnknownArgumentType]
        PROJECT_ID,
    )
    try:
        # Create the Secret Container if it doesn't already exist
        secrets.create_secret(SECRET_ID)
    except AlreadyExists:
        pass
    _ = secrets.add_secret_version(
        SECRET_ID, json.dumps({"installed_secret": local_json["installed"]}, indent=2)
    )


if __name__ == "__main__":
    main()
