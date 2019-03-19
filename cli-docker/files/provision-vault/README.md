# Provisioning a Dummy Vault and Postgres for Testing

We provision the test vault using these scripts.  This has been inspired by
[Codifying Vault Policies and Configuration](https://www.hashicorp.com/blog/codifying-vault-policies-and-configuration.html).
Note however that we are also putting in secrets in this provisioning which certainly is not good practice.

# Data for the postgres

The script and data files are in the postgres directory.
create user test1 password 'pw1';
psql -d postgres -U test1

postgres=> select * from testtable;
ERROR:  permission denied for table testtable
# psql -U postgres
psql (11.1 (Debian 11.1-3.pgdg90+1))
Type "help" for help.

postgres=# grant all privileges on table testtable to test1;
GRANT
postgres=# \q
# psql -d postgres -U test1
psql (11.1 (Debian 11.1-3.pgdg90+1))
Type "help" for help.

postgres=> select * from testtable;
 id |  name  
----+--------
  1 |  name1
  2 |  name2
  3 |  name3
(3 rows)

