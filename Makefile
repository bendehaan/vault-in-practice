up:
	docker-compose up

clean:
	docker-compose down
	# docker-compose down does not remove the volumes
	docker volume rm vault-in-practice_vaultfile
	docker volume rm vault-in-practice_vaultlogs
