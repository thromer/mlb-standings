import argparse

import google.auth
from google.auth.transport.requests import AuthorizedSession

from mlbstandings import light_google_wrappers


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and print a secret from Google Secret Manager using ADC."
    )
    _ = parser.add_argument("--project", required=True, help="Google Cloud project ID")
    _ = parser.add_argument("--secret", required=True, help="Secret ID to fetch")
    _ = parser.add_argument(
        "--version", default="latest", help="Secret version to fetch (default: latest)"
    )

    args = parser.parse_args()

    # Use Application Default Credentials
    credentials, _ = google.auth.default(  # pyright:ignore[reportUnknownVariableType,reportUnknownMemberType]
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)  # pyright:ignore[reportUnknownArgumentType]

    secrets = light_google_wrappers.Secrets(session, args.project)  # pyright:ignore[reportAny]

    try:
        secret_data = secrets.access_secret_version(args.secret, args.version)  # pyright:ignore[reportAny]
        print(secret_data)
    except Exception as e:
        print(f"Error fetching secret: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
