import json

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import (  # pyright: ignore[reportMissingTypeStubs]
    InstalledAppFlow,
)

from mlbstandings import light_google_wrappers


# TODO: get these from constants.py
PROJECT_ID = "mlb-standings-001"
SECRET_ID = "creds"
SCOPES = [
    "https://www.googleapis.com/auth/drive",  # Need broad scope to copy
    "https://www.googleapis.com/auth/spreadsheets",
]


def main():
    secrets = light_google_wrappers.Secrets(
        AuthorizedSession(google.auth.default()[0]),  # pyright:ignore[reportUnknownMemberType,reportUnknownArgumentType]
        PROJECT_ID,
    )
    creds_data = json.loads(secrets.access_secret_version(SECRET_ID))

    if (
        "installed_secret" not in creds_data
        or "client_id" not in creds_data["installed_secret"]
        or "client_secret" not in creds_data["installed_secret"]
    ):
        msg = f"'installed_secret.client_id' and/or 'installed_secret.client_secret' missing from {SECRET_ID}"
        raise RuntimeError(msg)

    flow = InstalledAppFlow.from_client_config(  # pyright: ignore[reportUnknownMemberType]
        {"installed": creds_data["installed_secret"]},
        SCOPES,
    )
    creds_data["refresh_token"] = flow.run_local_server(port=0).refresh_token  # pyright: ignore[reportUnknownMemberType]
    _ = secrets.add_secret_version(SECRET_ID, json.dumps(creds_data, indent=2))


if __name__ == "__main__":
    main()
