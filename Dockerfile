# Build

# We use the same image as the runtime base image so that Python
# version and location matches. Might save on data transfer costs.
FROM us-west1-docker.pkg.dev/serverless-runtimes/google-22/runtimes/python313 AS builder

# Sorta hacky solution to being able to write to /workspace
USER root

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /workspace

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_MANAGED_PYTHON=1

COPY . .
RUN uv sync --frozen --no-dev --no-editable

# Run
FROM scratch
COPY --from=builder /workspace/.venv /workspace/.venv

ENV PYTHONPATH=/workspace/.venv/lib/python3.13/site-packages
ENV PATH=/workspace/.venv/bin:$PATH

CMD ["serve"]
