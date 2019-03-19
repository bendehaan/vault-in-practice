import click
import logging
import os
import psycopg2
import time
import yaml
from logging.config import dictConfig

from py_de_vault import settings, VaultManager


# Fix click error on incorrectly configured locale
import locale, codecs
# locale.getpreferredencoding() == 'ANSI_X3.4-1968'
if codecs.lookup(locale.getpreferredencoding()).name == 'ascii':
    os.environ['LANG'] = 'en_US.utf-8'

# general setup
with open("logging.yaml") as log_conf_file:
    log_conf = yaml.safe_load(log_conf_file)
    dictConfig(log_conf)

log = logging.getLogger("example")


@click.group()
def cli():
    pass


@click.command()
@click.option("--token")
def get_secret(token):
    log.info("getting secret")
    # setup of VaultManager
    settings.configure(vault_addr=os.environ.get("VAULT_ADDR"))
    settings.configure(vault_token=token)
    settings.configure(vault_refresh_seconds=5)
    vm = VaultManager(scope="deptest1", secret_keys=["secret1"])
    vm.monitor_secrets()
    log.info(f'Retrieved secret {vm.get_secret("secret1", just_data=False)}')
    log.info(f'Retrieved secret {vm.get_secret("secret1")}')
    time.sleep(30)  # in this period can update secret through the ui
    log.info(f'Retrieved secret {vm.get_secret("secret1")}')


def new_connection(secrets):
    """Given updated secrets, create a new connection.
    """
    creds = secrets['db_credentials']['data']['data']
    log.info(f"Making new connection with {creds}")
    # Note: obviously this doesn't close the previous connection; best use a connection pool manager
    conn = psycopg2.connect(host="db", user=creds['login'], password=creds['password'])
    return conn


@click.command()
@click.option("--token")
def get_connection(token):
    log.info("getting connection")
    # setup of VaultManager
    settings.configure(vault_addr=os.environ.get("VAULT_ADDR"))
    settings.configure(vault_token=token)
    settings.configure(vault_refresh_seconds=5)
    vm = VaultManager(scope="deptest1", secret_keys=["db_credentials"])
    vm.monitor_secrets()
    log.info(f"credentials {vm.get_secret('db_credentials')}")
    vm.manage_update("connection", ["db_credentials"], new_connection)

    conn = vm.get_secret("connection")   # this connection is already set up using the latest secrets
    cur = conn.cursor()
    cur.execute("SELECT * from testtable")
    print(cur.fetchall())
    conn.close()


cli.add_command(get_secret, name="get")
cli.add_command(get_connection, name="connection")

if __name__ == "__main__":
    cli()
