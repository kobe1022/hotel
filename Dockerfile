# syntax=docker.io/docker/dockerfile-upstream:1.27.0
# check=error=true

# Aufruf:   docker build --tag gast:0.1.0-hardened .
#               ggf. --no-cache
#
#           Windows:   Get-Content Dockerfile | docker run --rm --interactive hadolint/hadolint:v2.15.1-debian
#           macOS:     cat Dockerfile | docker run --rm --interactive hadolint/hadolint:v2.15.1-debian
#
#           docker debug gast:0.1.0-hardened
#           docker scout sbom gast:0.1.0-hardened
#           docker scout cves gast:0.1.0-hardened
#           docker save gast:0.1.0-hardened > gast.tar
#           docker scout attest get dhi.io/python:3.15.0-debian13 --predicate-type https://slsa.dev/provenance/v0.2 --verify
#               https://docs.docker.com/dhi/core-concepts/slsa

# https://docs.docker.com/engine/reference/builder/#syntax
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md
# https://hub.docker.com/r/docker/dockerfile
# https://docs.docker.com/build/building/multi-stage
# https://docs.docker.com/dhi
# https://testdriven.io/blog/docker-best-practices
# https://containers.gitbook.io/build-containers-the-hard-way
# https://wiki.debian.org/DebianReleases
# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# https://www.saaspegasus.com/guides/uv-deep-dive

# ARG: "build-time" Variable
# ENV: "build-time" und "runtime" Variable
ARG PYTHON_MAIN_VERSION=3.15
# ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}.0   # Patch-Tag "3.15.0" bei dhi.io noch nicht vorhanden
ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}
# ARG UV_VERSION=0.12.20   # zu alt: hat fuer python3.15 nur RC-Tags, kein "-dhi"
ARG UV_VERSION=0.13.6

# ------------------------------------------------------------------------------
# S t a g e   b u i l d e r
# ------------------------------------------------------------------------------
# uv-Image fuer Python 3.15 gibt es noch nicht als "-dhi"-Variante, daher wird uv separat
# bereitgestellt. Sobald es "uv:${UV_VERSION}-python${PYTHON_MAIN_VERSION}-dhi" gibt, kann
# der Builder wieder direkt darauf basieren (ohne die Stage "uv" und das COPY unten).
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# Builder und final sind beide dhi.io/python (Debian 13), damit die Pfade zu Python im Venv
# in beiden Stages uebereinstimmen (/usr/bin/python).
FROM dhi.io/python:${PYTHON_VERSION}-debian13-dev AS builder

COPY --from=uv /uv /uvx /usr/local/bin/

WORKDIR /opt/app

# pyinstrument baut eine C-Extension aus dem Quellpaket (fuer Python 3.15 noch kein Wheel) -> gcc noetig
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
# Copy from the cache instead of linking since it's a mounted volume
# Kein Python-Download erforderlich
# https://github.com/astral-sh/uv/issues/8635#issuecomment-2759670742
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_MANAGED_PYTHON=true \
    UV_SYSTEM_PYTHON=true \
    UV_PROJECT_ENVIRONMENT=/opt/app/.venv

RUN ["/usr/local/bin/uv", "venv"]

# .venv erstellen und "Dependencies" installieren
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    ["/usr/local/bin/uv", "sync", "--frozen", "--no-install-project", "--no-default-groups", "--no-editable"]

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY LICENSE README.md pyproject.toml ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    ["/usr/local/bin/uv", "sync", "--frozen", "--no-default-groups", "--no-editable"]

# ------------------------------------------------------------------------------
# S t a g e   f i n a l
# ------------------------------------------------------------------------------
FROM dhi.io/python:${PYTHON_VERSION}-debian13 AS final

# docker image inspect dhi.io/python:${PYTHON_VERSION}-debian13 --format '{{.Config.User}}'
# $cid = docker create dhi.io/python:${PYTHON_VERSION}-debian13
# docker export $cid | tar -xOf - etc/group
# docker rm $cid
ARG NONROOT_UID=65532
ARG NONROOT_GID=65532

# Anzeige bei "docker inspect ..."
# https://specs.opencontainers.org/image-spec/annotations
# https://spdx.org/licenses
# MAINTAINER ist deprecated https://docs.docker.com/engine/reference/builder/#maintainer-deprecated
LABEL org.opencontainers.image.title="gast" \
    org.opencontainers.image.description="Appserver gast mit Basis-Image Trixie hardened" \
    org.opencontainers.image.version="0.1.0-hardened" \
    org.opencontainers.image.licenses="GPL-3.0-or-later" \
    org.opencontainers.image.authors="Benjamin Koeken, Aaron Stief"

# "working directory" fuer die Docker-Kommandos RUN, ENTRYPOINT, CMD, COPY und ADD
WORKDIR /opt/app

USER ${NONROOT_UID}:${NONROOT_GID}

COPY --from=builder --chown=${NONROOT_UID}:${NONROOT_GID} /opt/app ./

# Place executables in the environment at the front of the path
ENV PATH="/opt/app/.venv/bin:$PATH"

EXPOSE 8000

STOPSIGNAL SIGINT

ENTRYPOINT ["python", "-m", "gast"]
