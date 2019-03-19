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


## 3. Initializing & unsealing Vault

* Run w/ backend Vault through docker-compose (contains volume)
* Init
* Bring it down
* Bring it up again
* Unseal

## 4. Authenticating to vault

* Setting the token securely

## Using VaultManager

First we provision the vault by (in the client container) going into the directory /provision-vault/ first defining
the token

    export VAULT_TOKEN=s.y6Ky8WAfvEePyAxRHncSQ2Aa
    
and then provisioning the vault using

    ./provision.sh
    
Now go to localhost:8200 log in with the token.  In the cli container go to directory /vaultmanager/.  In that
directory run

    make getsecret
    
you then see the value of the secret.  In the ui, go to update the secret.  If you do it quick enough you will
see the last line have the updated secret.

Then do

    make connection

# Notes

## docker compose

In the docker compose file we set up three containers (1) client, the container in which we will be executing our
commands (think of this as being a local shell on your laptop where all needed tools are already installed), (2) vault,
this is the running vault service storing its data in a volume and exposing a port on your computer locally in case
you want to interact with it using an installed vault binary, and (3) a postgres container for the demo with dynamic
secrets.

The postgres container has its configuration in two places, (1) in the docker compose file, (2) in the directory
postgres/ which gets mounted into that container.  In this directory there is some test data so that we already have
a filled database to play with.
