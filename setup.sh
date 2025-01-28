echo "setup range wars"
sudo service postgresql restart
echo "drop range wars db: enter db password"
dropdb range_wars -U dbadmin -h localhost -i -p 5433
echo "create database: enter db password"
createdb -h localhost -p 5433 -U dbadmin -O dbadmin range_wars
echo "restore database: enter db password"
pg_restore -v --no-owner --role=dbowner --host=localhost --port=5433 --username=dbadmin --dbname=range_wars database_dumps/range_wars.sql