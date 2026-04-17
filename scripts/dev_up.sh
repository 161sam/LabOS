#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
mkdir -p storage/wiki storage/photos

docker compose up --build
