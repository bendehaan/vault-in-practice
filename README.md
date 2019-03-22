# Vault Workshop

In following this outline you will:

1. Start a Vault environment using docker-compose (see [notes](#notes))
2. Do basic Vault operations
3. Create a dynamic secret
4. Use the transit secret backend
5. Use VaultManager as wrapper

## Requirements

* Docker
* Docker compose
  * If you haven't got docker compose, installing it through pip is the easiest option.

## Running Vault

- To start vault and the other used docker containers run (make up) in the directory containing the docker-compose.yaml
  file

      docker-compose up

  this starts up 3 containers (client, vault, and postgres).  Can see this with 'docker ps'

      CONTAINER ID        NAMES                        IMAGE                      STATUS
      3bad8be2d9d6        vault-in-practice_vault_1    vault:1.1.0-beta2          Up 14 hours
      4cd80e52d798        vault-in-practice_db_1       postgres:10.4              Up 14 hours
      bf1a84a0cf0d        vault-in-practice_client_1   kasterma/vip:0.0.0         Up 14 hours

- We will run all our commands from the client container that has been started.  In a new terminal type (make exec)

       docker exec -ti vault-in-practice_client_1 bash
  
  this will give you a bash shell in the client container where we will execute all the commands.  Think of this shell
  as the local shell on your laptop (but with everything you need installed).
  
- `vault status` will now show that this vault is not initialized and is still sealed.
  
- `vault operator init`

      Unseal Key 1: C85vMOVjVGrfCRMttk2Kfgg93upYCVb4SmBRf+sPYhv0
      Unseal Key 2: Hp/LbMLwGN4jwOjcDr/uHCicVtv4e+yalo1KdnbTNmyQ
      Unseal Key 3: oX3I/Jkgxny+8HUwT2kfA0T3Yv8TPt9vTtPJjhUfK+ri
      Unseal Key 4: B6fzcpvdEC+JBziv8xyK89JkTKlY6riwQ+0fsBpuejEo
      Unseal Key 5: NZV2tz31AfmQdq2LzPotLSUrpTFD70es9Tc/fY/XJ0ol
    
      Initial Root Token: s.LtwAGw2b9wvvP4iKZHEa1Fwn

Make sure you keep this info handy.  **If you lose it you will need to start over.**

- `vault operator unseal` repeatedly with the info above.  After having done this three times you will see that the vault is both initialized and unsealed.

- Check everything is working; in the client bash run

       vault status
    
  and you should see an output of the form:
  
        Key             Value
        ---             -----
        Seal Type       shamir
        Initialized     true
        Sealed          false
        Total Shares    1
        Threshold       1
        Version         1.1.0-beta2
        Cluster Name    vault-cluster-47145d50
        Cluster ID      2864e1a8-7623-34d0-b9b6-ddde52e138b6
        HA Enabled      false

### Important note

The data is stored on docker volumes.  So you can stop all containers (docker-compose down) and as long as you don't delete the volumes the data will be maintained.  Then when you start it back up, you need your unseal keys to be able to use it. Running `make clean` will remove all data.

## Basic Vault operations

- Get a shell in the client container (make exec)

      docker exec -ti vault-in-practice_client_1 bash

- `vault status` - check if everything's okay.
- `vault login` use the root token from the log, now the token gets stored in '/root/.vault-token' (the user in the
   container is root :-/ Bonus points if you can explain why this is bad practice!)

### Key value store

- `vault secrets enable -version=2 -path=secret kv` enable the kv secrets engine; note this is the engine that is
   enabled by default in when running in --dev mode.  It is a versioned key-value store that takes care of encryption
   before storing in non-volatile storage, and access management through policies (later).

- `vault kv put secret/workshop foo=bar` - create a secret (note that this is bad practice since it'll show up in your shell history).
- `vault kv get secret/workshop` - retrieve the secret
- `vault kv put secret/workshop foo=barbar` - store new version of secret
- `vault kv get secret/workshop` - retrieve the secret again and note the version
- `vault kv get --version=1 secret/workshop` get an older version

- `curl --header "X-Vault-Token: $(cat /root/.vault-token)" ${VAULT_ADDR}/v1/secret/data/workshop` to request the
  secret using the API (really the above vault cli commands are translated to such requests); see
  https://www.vaultproject.io/api/secret/kv/kv-v2.html for the full description of the key-value store API.
  
- `curl --header "X-Vault-Token: $(cat /root/.vault-token)" ${VAULT_ADDR}/v1/secret/data/workshop?version=1`

- open browser to `localhost:8200/ui`.  Use your token to login, go to the secret and update to a new version.  This is
  again doing the same thing as the curl command, but in a more point and click way.

- `vault kv put secret/hello foo=bar` create four versions of a secret.
- `vault kv put secret/hello foo=barr`
- `vault kv put secret/hello foo=barrr`
- `vault kv put secret/hello foo=barrrr`
- `vault kv destroy -versions=2 secret/hello` this destroys the second version of the secret

### Authentication and Policies

- `vault auth list` - retrieve the list of enabled authentication options
- `vault policy write test policy1.hcl` add a new policy that gives full access to only secrets that start with workshop.
- `vault auth enable userpass` this is using the API at https://www.vaultproject.io/api/auth/userpass/index.html, we
  are showing this here, but all interaction with Vault is through API described like this
- `vault write auth/userpass/users/workshop password="workshop" policies="test"` - create a user bound to the previously created policy
- `vault login -method=userpass username=workshop password=workshop` login as the newly created user
- `vault auth list` see we now have more methods enabled
- `vault kv get secret/hello` permission denied
- `vault kv get secret/workshop`
- `vault kv put secret/workshop foo=bar`

- `vault token lookup` retrieve info about your token and associated policies

### Transit Secrets Engine

https://learn.hashicorp.com/vault/encryption-as-a-service/eaas-transit

Note: this requires the vaul to be provisioned by going to `/provision-vault/` in the cli container and running
`./provision.sh`.

You can check that the provisioning is correct by checking for the existence of the transitpol by running
`vault policy read transitpol`.

- `vault secrets enable transit` enable the transit secrets engine.

- `vault write -f transit/keys/orders` create an encryption key ring named `orders`.

- `plain="4111 1111 1111 1111"`

- `plaintext=$(base64 <<< ${plain})` we first base64 encode the text, since then the plaintext is safe to be sent as
  part of http request or reply.

- `vault write transit/encrypt/orders plaintext=$plaintext` encrypt it.  Note that Vault is not storing the data, it
  only stores the keys and arranges access to the keys through policies, the user manages the data.

- `cipher=$(vault write transit/encrypt/orders plaintext=$plaintext -format=json)` encrypt it again, but now get json
  output and store in variable cipher.
  
- equivalently

      curl --header "X-Vault-Token: $VAULT_TOKEN" \
           --request POST \
           --data '{"plaintext": "NDExMSAxMTExIDExMTEgMTExMQo="}' \
           http://vault:8200/v1/transit/encrypt/orders

  which shows how easy it is to use from an application (note that you can always get the curl equivalent by running
  `vault write -output-curl-string transit/encrypt/orders plaintext=$plaintext`; note `-output-curl-string` should work
  for most if not all vault commands).

- `ciphertext=$(echo $cipher | jq -r .data.ciphertext)`

- `vault write transit/decrypt/orders ciphertext=$ciphertext` decrypt the ciphertext you just created.

- equivalently

      curl --header "X-Vault-Token: $VAULT_TOKEN" \
           --request POST \
           --data '{"ciphertext": "$ciphertext"}' \
       http://vault:8200/v1/transit/decrypt/orders

## Dynamic postgres secret

https://www.vaultproject.io/docs/secrets/databases/postgresql.html

- `vault secrets enable database`
- create the dynamic secret

        vault write database/config/vaultpg \
            plugin_name=postgresql-database-plugin \
            allowed_roles="create" \
            connection_url="postgresql://{{username}}:{{password}}@db:5432/vaultpg?sslmode=disable" \
            username="vaultpg" \
            password="monkey123"

        vault write database/roles/create \
            db_name=vaultpg \
            creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
                GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
            default_ttl="1h" \
            max_ttl="24h"

- `vault read database/creds/create` to get freshly created credentials. Note the lease duration and whether it's renewable.

- psql -h db -U [username from above] -d vaultpg

## Using VaultManager

Note this requires

1. the step of enabling the kv store above to have been done before (`vault secrets enable -version=2 -path=secret kv`).

2. the vault being provisioned (`./provision.sh` in directory /provision-vault/).

Now go to localhost:8200 log in with the token.  In the cli container go to directory `/vaultmanager/`.  In that
directory first update the VAULT_TOKEN in the Makefile, and then run

    make getsecret

You then see the value of the secret.  In the ui, go to update the secret.  If you do it quick enough you will see the last line have the updated secret.  Inspect `vaultmanager/example.py` function `get_secret` to see how the VaultManager is used.

Then do

    make connection

there you see some data extracted from the database (compare with postgres/data/testtable.csv).  Now inspect `vaultmanager/exmaple.py` function `get_connection` to see how the VaultManager is used.  Note that the connection is a derived secret that is automatically updated by the VaultManager when the credentials as stored in vault are updated.

# Notes

## docker compose

In the docker compose file we set up three containers (1) client, the container in which we will be executing our
commands (think of this as being a local shell on your laptop where all needed tools are already installed), (2) vault,
this is the running vault service storing its data in a volume and exposing a port on your computer locally in case
you want to interact with it using an installed vault binary or use the vault ui (localhost:8200) for updating secrets,
and (3) a postgres container for the demo with dynamic secrets (and also used as an example for automatically updated
derived "secret" in the vault manager).

The postgres container has its configuration in two places, (1) in the docker compose file, (2) in the directory
postgres/ which gets mounted into that container.  In this directory there is some test data so that we already have
a filled database to play with.

## Provisioning in the VaultManager step

In the cli-docker (directory cli-docker/files/provision-vault in this repo) you see a use of the pattern suggested
at https://www.hashicorp.com/blog/codifying-vault-policies-and-configuration, but with also some secrets added (which
clearly should not be managed in this way).  It consists of a directory structure that mirrors the api structure of
vault, and a shell script (provision.sh) that sends the data in the appropriate order to vault to configure it.
