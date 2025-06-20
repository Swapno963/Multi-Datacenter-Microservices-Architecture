up:
	docker-compose up -d 
down:
	docker-compose down

logs:
	docker-compose logs -f	

rebuild:
	docker-compose build --volues
	docker-compose up -d