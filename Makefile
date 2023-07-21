run r:
	docker compose up -d --build

init i:
	chmod +x push_connectors.sh && ./push_connectors.sh

stop s:
	docker compose down --remove-orphans

redis-cli rc:
	docker exec -it my-redis redis-cli

insert-data id:
	curl http://localhost:5000/insert

list-data ld:
	curl http://localhost:5000/list

connect-logs cl:
	docker compose logs connect -f 

kafka-logs kl:
	docker compose logs broker -f

python-logs pl:
	docker compose logs python-script -f
