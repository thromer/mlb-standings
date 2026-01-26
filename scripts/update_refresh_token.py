import json

from google.cloud.secretmanager import SecretManagerServiceClient
from google_auth_oauthlib.flow import (  # pyright: ignore[reportMissingTypeStubs]
    InstalledAppFlow,
)


# TODO: get these from constants.py
PROJECT_ID = "mlb-standings-001"
SECRET_ID = "creds"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]


def main():
    client = SecretManagerServiceClient()
    secret_name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})  # pyright: ignore[reportUnknownMemberType]
    creds_data = json.loads(response.payload.data.decode("UTF-8"))  # pyright: ignore[reportAny]

    if (
        "installed_secret" not in creds_data
        or "client_id" not in creds_data["installed_secret"]
        or "client_secret" not in creds_data["installed_secret"]
    ):
        msg = f"'installed_secret.client_id' and/or 'installed_secret.client_secret' missing from {secret_name}"
        raise RuntimeError(msg)

    flow = InstalledAppFlow.from_client_config(  # pyright: ignore[reportUnknownMemberType]
        {"installed": creds_data["installed_secret"]},
        SCOPES,
    )
    creds_data["refresh_token"] = flow.run_local_server(port=0).refresh_token  # pyright: ignore[reportUnknownMemberType]
    _ = client.add_secret_version(  # pyright: ignore[reportUnknownMemberType]
        request={
            "parent": f"projects/{PROJECT_ID}/secrets/{SECRET_ID}",
            "payload": {"data": json.dumps(creds_data, indent=2).encode("UTF-8")},
        }
    )


if __name__ == "__main__":
    main()
