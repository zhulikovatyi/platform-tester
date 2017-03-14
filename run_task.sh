#!/usr/bin/env bash
cat config/credentials | python scripts/client.py "$@"