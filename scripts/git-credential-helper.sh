#!/bin/sh
# Usage: git config credential.helper /path/to/scripts/git-credential-helper.sh
case "$1" in
    get)
        TOKEN=$(grep -A3 Jrink525 /home/node/.openclaw/gh-config/hosts.yml | grep oauth_token | head -1 | awk '{print $2}')
        echo "username=Jrink525"
        echo "password=${TOKEN}"
        ;;
esac
