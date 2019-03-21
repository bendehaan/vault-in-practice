#!/usr/bin/env bash
set -e

shopt -s nullglob

export VAULT_TOKEN=${VAULT_TOKEN:-$(vault print token)}

echo TOK ${VAULT_TOKEN}

function provision() {
  set +e
  pushd "$1" > /dev/null
  for f in $(ls "$1"/*.json); do
    p="$1/${f%.json}"
    echo "Provisioning $p"
      #--silent \
      #--fail \
    curl \
      --location \
      --header "X-Vault-Token: ${VAULT_TOKEN}" \
      --data @"${f}" \
      "${VAULT_ADDR}/v1/${p}"
  done
  popd > /dev/null
  set -e
}

echo "Verifying Vault is unsealed"
vault status > /dev/null

pushd data >/dev/null
provision sys/auth
#provision sys/mounts
provision sys/policy
#provision postgresql/config
#provision postgresql/roles
provision auth/userpass/users
provision secret/data/deptest1
popd > /dev/null
