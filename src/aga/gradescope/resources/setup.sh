#!/usr/bin/env bash

set -euo pipefail

apt-get install python -y
apt-get install python-pip -y

python3 -m pip install aga
