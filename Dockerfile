# Build

# We use the same image as the runtime base image so that Python
# version and location matches. Might save on data transfer costs.
# -full for c++ for grpcio for grpc-iam-v1 for google-cloud-secret-manager
FROM us-west1-docker.pkg.dev/serverless-runtimes/google-24/runtimes/python314 AS builder

# Sorta hacky solution to being able to write to /workspace
USER root

RUN apt-get update && apt-get install -y build-essential

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /workspace

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_MANAGED_PYTHON=1

# Separate layer just for grpcio for caching though pyproject.toml changes will probably invalidate it
COPY pyproject.toml uv.lock ./
RUN uv add grpcio --no-sync
RUN uv sync --frozen --no-dev --no-editable --no-install-project

COPY . .
RUN uv sync --frozen --no-dev --no-editable

# Run
FROM scratch
COPY --from=builder /workspace/.venv /workspace/.venv

ENV PYTHONPATH=/workspace/.venv/lib/python3.14/site-packages
ENV PATH=/workspace/.venv/bin:$PATH

CMD ["serve"]
