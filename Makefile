.PHONY: up down test test-cov logs clean

# Запуск всех сервисов (с тестами)
up:
	docker-compose up -d

# Запуск только приложения (без тестов)
up-app:
	docker-compose up -d postgres app pgadmin

# Остановка всех сервисов
down:
	docker-compose down

# Остановка с удалением volumes
down-clean:
	docker-compose down -v

# Запуск тестов
test:
	docker-compose up tests

# Запуск тестов с покрытием
test-cov:
	docker-compose run tests pytest --cov=app tests/

# Просмотр логов
logs:
	docker-compose logs -f

# Очистка
clean:
	docker-compose down -v
	docker system prune -f

# Перезапуск с тестами
restart: down up

# Быстрый перезапуск приложения
restart-app:
	docker-compose restart app