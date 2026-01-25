import argparse
import json
from typing import cast

from google.api_core.exceptions import AlreadyExists
from google.cloud.secretmanager import SecretManagerServiceClient


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
    client = SecretManagerServiceClient()
    try:
        # Create the Secret Container if it doesn't already exist
        _ = client.create_secret(  # pyright: ignore[reportUnknownMemberType]
            request={
                "parent": f"projects/{PROJECT_ID}",
                "secret_id": SECRET_ID,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    except AlreadyExists:
        pass
    _ = client.add_secret_version(  # pyright: ignore[reportUnknownMemberType]
        request={
            "parent": f"projects/{PROJECT_ID}/secrets/{SECRET_ID}",
            "payload": {
                "data": json.dumps(
                    {"installed_secret": local_json["installed"]}, indent=2
                ).encode("UTF-8")
            },
        }
    )


if __name__ == "__main__":
    main()
