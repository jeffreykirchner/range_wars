echo "Dump Database"
pg_dump --host=localhost --port=5432 --username=dbadmin --dbname=range_wars --file=database_dumps/range_wars.sql -v -Fc