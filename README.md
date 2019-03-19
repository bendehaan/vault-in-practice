# Vault Workshop

## Running Vault

- To start vault and the other used docker containers run

    docker-compose up

- We will run all our commands from the client container that has been started.  In a new terminal type
 
       docker exec -ti vault-in-practice_client_1 bash

- Check everything is working; in the client bash run

       vault status
    
  and you should see an output of the form
  
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

- In the terminal where you run docker-compose up there is some logging information.  In particular there are two lines
  of the form:
  
      vault_1   | Unseal Key: #################
      vault_1   | Root Token: #################
      
  Note down both these tokens, they are essential for what follows.

## Basic Vault operations

- Get a shell in the client container

     docker exec -ti vault-in-practice_client_1 bash

- 'vault status'
- 'vault login' use the root token from the log
- 'vault kv put secret/workshop foo=bar'
- 'vault kv get secret/workshop'
- 'vault kv put secret/workshop foo=barbar'
- 'vault kv get secret/workshop'
- 'vault kv get --version=1 secret/workshop/one' get an older version

- 'vault kv put secret/hello foo=bar' create four versions of a secret
- 'vault kv put secret/hello foo=barr'
- 'vault kv put secret/hello foo=barrr'
- 'vault kv put secret/hello foo=barrrr'
- 'vault kv destroy -versions=2 secret/hello' this destroys the second version of the secret

- 'vault policy write test policy1.hcl'
- 'vault auth enable userpass' this is using the API at https://www.vaultproject.io/api/auth/userpass/index.html, we
  are showing this here, but all interaction with Vault is through API described like this
- 'vault write auth/userpass/users/workshop password="workshop" policies="test"'
- 'vault login -method=userpass username=workshop password=workshop' login as the newly created user
- 'vault kv get secret/hello' permission denied
- 'vault kv get secret/workshop'
- 'vault kv put secret/workshop foo=bar'

## 3. Initializing & unsealing Vault

* Run w/ backend Vault through docker-compose (contains volume)
* Init
* Bring it down
* Bring it up again
* Unseal

## 4. Authenticating to vault

* Setting the token securely

## Dynamic postgres secret

https://www.vaultproject.io/docs/secrets/databases/postgresql.html

- 'vault secrets enable database'
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

- 'vault read database/creds/create' to get freshly created credentials

- psql -h db -U v-root-create-es6wKLxlCagkQS9Gc9dN-1553011618 -d vaultpg

## Using VaultManager

First we provision the vault by (in the client container) going into the directory /provision-vault/ first defining
the token

    export VAULT_TOKEN=s.fRiC5c78dJZ5Xvn5QmXnPai5
    
and then provisioning the vault using

    ./provision.sh
    
Now go to localhost:8200 log in with the token.  In the cli container go to directory /vaultmanager/.  In that
directory first update the VAULT_TOKEN in the Makefile, and then run

    make getsecret
    
you then see the value of the secret.  In the ui, go to update the secret.  If you do it quick enough you will
see the last line have the updated secret.

Then do

    make connection

there you see some data extracted from the database (compare with postgres/data/testtable.csv).

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
