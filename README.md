# Organization Catalog API 🏢

REST API приложение для справочника организаций, зданий и видов деятельности. Реализовано на FastAPI с PostgreSQL, включает полный CRUD функционал, геопоиск и древовидную структуру видов деятельности.

## 🚀 Возможности

- **Организации** - полное управление организациями с телефонами и видами деятельности
- **Здания** - управление зданиями с географическими координатами
- **Виды деятельности** - древовидная структура с ограничением вложенности (3 уровня)
- **Геопоиск** - поиск организаций и зданий в радиусе/прямоугольной области
- **REST API** - каноничные RESTful эндпоинты с документацией Swagger
- **Аутентификация** - защита API с помощью статического API ключа
- **Тестирование** - полное покрытие тестами с автоматической проверкой при запуске

## 🛠 Технологический стек

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Containerization**: Docker, Docker Compose
- **Documentation**: Swagger UI, ReDoc

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+

## 🏃‍♂️ Быстрый старт

### Автоматический запуск с тестами

```bash
# Клонируем репозиторий
git clone <repository-url>
cd organization_catalog

# Запускаем всю систему (с автоматическим тестированием)
docker-compose up -d
```

Система автоматически:
1. 🐘 Запускает PostgreSQL
2. 🧪 Выполняет все тесты
3. ✅ При успешных тестах запускает приложение
4. 🚀 Разворачивает полную среду

### Доступ к приложению

После успешного запуска:

- **API**: http://localhost:8000
- **Документация Swagger**: http://localhost:8000/docs
- **Альтернативная документация**: http://localhost:8000/redoc
- **PGAdmin** (управление БД): http://localhost:8080

### Учетные данные

- **API Key**: `test-api-key-123` (заголовок `X-API-Key`)
- **PGAdmin**: `admin@orgcatalog.com` / `admin`
- **База данных**: `catalog_user` / `catalog_password`

## 🧪 Тестирование

### Автоматические тесты

Тесты выполняются автоматически при запуске через `docker-compose up -d`. Если тесты не проходят, приложение не запускается.

### Ручной запуск тестов

```bash
# Запуск только тестов
docker-compose up tests

# Тесты с покрытием кода
docker-compose run tests pytest --cov=app tests/

# Конкретный тестовый файл
docker-compose run tests pytest tests/test_organizations.py -v

# Тесты с подробным выводом
docker-compose run tests pytest -v --tb=long
```

### Запуск без тестов

```bash
# Запуск только приложения (пропускает тесты)
docker-compose up -d postgres app pgadmin
```

## 📚 API Документация

### Аутентификация

Все защищенные эндпоинты требуют API ключ в заголовке:
```http
X-API-Key: test-api-key-123
```

### Основные эндпоинты

#### 🏢 Организации

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/organizations/` | Список организаций с фильтрацией |
| `GET` | `/api/v1/organizations/{id}` | Детальная информация об организации |
| `POST` | `/api/v1/organizations/` | Создание организации |
| `PUT` | `/api/v1/organizations/{id}` | Обновление организации |
| `DELETE` | `/api/v1/organizations/{id}` | Удаление организации |

**Параметры фильтрации:**
- `activity_id` - фильтр по виду деятельности (включая дочерние)
- `name` - поиск по названию организации
- `in_area` - поиск в географической области

**Примеры запросов:**
```bash
# Поиск по виду деятельности
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/organizations/?activity_id=1"

# Поиск по названию
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/organizations/?name=Рога"

# Поиск в радиусе
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/organizations/?in_area=circle:55.7558,37.6173,1000"

# Создание организации
curl -X POST -H "X-API-Key: test-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая организация",
    "building_id": 1,
    "phone_numbers": [{"number": "123-456-789"}],
    "activity_ids": [1, 2]
  }' \
  "http://localhost:8000/api/v1/organizations/"
```

#### 🏛️ Здания

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/buildings/` | Список всех зданий |
| `GET` | `/api/v1/buildings/{id}` | Детальная информация о здании |
| `GET` | `/api/v1/buildings/{id}/organizations` | Организации в здании |
| `GET` | `/api/v1/buildings/nearby` | Поиск зданий в области |

**Примеры запросов:**
```bash
# Поиск зданий в радиусе
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/buildings/nearby?lat=55.7558&lon=37.6173&radius=1000"

# Организации в здании
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/buildings/1/organizations"
```

#### 🌳 Виды деятельности

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/activities/` | Дерево видов деятельности |
| `GET` | `/api/v1/activities/{id}` | Детальная информация о виде деятельности |
| `POST` | `/api/v1/activities/` | Создание вида деятельности |
| `PUT` | `/api/v1/activities/{id}` | Обновление вида деятельности |
| `DELETE` | `/api/v1/activities/{id}` | Удаление вида деятельности |

**Примеры запросов:**
```bash
# Получение дерева деятельностей
curl -H "X-API-Key: test-api-key-123" \
  "http://localhost:8000/api/v1/activities/?maxDepth=3"

# Создание вида деятельности
curl -X POST -H "X-API-Key: test-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{"name": "Новый вид деятельности", "parent_id": 1}' \
  "http://localhost:8000/api/v1/activities/"
```

## 🗄 Структура базы данных

### Таблицы

- **buildings** - здания с координатами
- **activities** - виды деятельности (древовидная структура)
- **organizations** - организации
- **phone_numbers** - телефоны организаций
- **organization_activities** - связь многие-ко-многим организаций и видов деятельности

### Ограничения

- Максимальная глубина вложенности видов деятельности: **3 уровня**
- Уникальность имен видов деятельности на одном уровне
- Защита от циклических ссылок в дереве деятельностей

## 🔧 Разработка

### Локальная разработка

```bash
# Клонирование и настройка
git clone <repository-url>
cd organization_catalog

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest

# Запуск сервера разработки
uvicorn app.main:app --reload
```

### Структура проекта

```
organization_catalog/
├── app/
│   ├── api/              # API роутеры
│   ├── core/             # Конфигурация, БД, безопасность
│   ├── crud/             # Бизнес-логика (CRUD операции)
│   ├── models/           # SQLAlchemy модели
│   ├── migrations/       # Alembic миграции
│   ├── schemas/          # Pydantic схемы
│   └── main.py           # Точка входа
├── tests/                # Тесты
├── deploy/               # Тут докер
├── scripts/              # Вспомогательные скрипты
└── docker-compose.yml    # Docker конфигурация
```

### Добавление новых функций

1. Создайте модель в `app/models/`
2. Добавьте схемы в `app/schemas/`
3. Реализуйте CRUD операции в `app/crud/`
4. Создайте роутеры в `app/api/routes/`
5. Напишите тесты в `tests/`
6. Создайте миграцию: `alembic revision --autogenerate -m "description"`

## 🐳 Docker команды

```bash
# Запуск всей системы
docker-compose up -d

# Только определенные сервисы
docker-compose up -d postgres app

# Просмотр логов
docker-compose logs -f
docker-compose logs -f app
docker-compose logs -f tests

# Остановка
docker-compose down

# Остановка с очисткой volumes
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache

# Проверка статуса
docker-compose ps
```

## 🚀 Production развертывание

### Настройка окружения

Создайте `.env` файл:

```env
# Database
POSTGRES_SERVER=your_server
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_strong_password
POSTGRES_DB=organization_catalog

# Security
API_KEY=your_secure_api_key
API_KEY_NAME=X-API-Key

# App
PROJECT_NAME=Organization Catalog API
VERSION=1.0.0
```

### Рекомендации для production

1. **Измените API ключ** на случайный секретный ключ
2. **Настройте PostgreSQL** с резервным копированием
3. **Включите HTTPS** через reverse proxy (nginx)
4. **Настройте мониторинг** и логирование
5. **Используйте переменные окружения** для всех секретов

## 🐛 Поиск и устранение неисправностей

### Распространенные проблемы

**Тесты не проходят:**
```bash
# Запустите тесты с подробным выводом
docker-compose run tests pytest -v --tb=long

# Проверьте логи БД
docker-compose logs postgres
```

**Приложение не запускается:**
```bash
# Проверьте статус контейнеров
docker-compose ps

# Просмотрите логи
docker-compose logs app

# Проверьте, что БД запущена
docker-compose logs postgres
```

**Миграции не применяются:**
```bash
# Принудительно примените миграции
docker-compose exec app alembic upgrade head
```

### Полезные команды

```bash
# Доступ к БД
docker-compose exec postgres psql -U catalog_user -d organization_catalog

# Shell в контейнере приложения
docker-compose exec app bash

# Перезапуск приложения
docker-compose restart app
```

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add some amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте документацию API: http://localhost:8000/docs
2. Просмотрите логи: `docker-compose logs`
3. Проверьте issues в репозитории проекта

---

**Happy Coding!** 🚀