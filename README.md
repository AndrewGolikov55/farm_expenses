# Farm Expenses Management System

## Описание проекта
**Farm Expenses Management System** – это веб-приложение для управления финансами фермерского хозяйства, позволяющее вести учет доходов, расходов, категорий и поставщиков в рамках одной организации.

Приложение построено на **Django** и поддерживает аутентификацию пользователей, управление организациями и детализированную аналитику финансов.

## Функциональность
- **Управление финансами**: Добавление, редактирование и удаление расходов и доходов.
- **Категории и поставщики**: Ведение списка категорий затрат и доходов, учет поставщиков.
- **Аналитика**: Визуализация динамики расходов и доходов, прогнозирование и отчетность.
- **Организации и пользователи**: Создание и управление организациями, роли пользователей.
- **REST API**: Поддержка API для интеграции с внешними сервисами.

## Стек технологий
- **Backend**: Django, Django REST Framework
- **Frontend**: Bootstrap 5, Chart.js
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker, Docker Compose
- **Аутентификация**: Django Auth

## Установка и запуск

### 1. Клонирование репозитория
```bash
$ git clone https://github.com/AndrewGolikov55/farm_expenses.git
$ cd farm_expenses
```

### 2. Настройка окружения
#### С помощью Docker (рекомендуемый способ)
```bash
$ docker compose -f docker/docker-compose.dev.yml up --build
```

#### Локально (без Docker)
Установите Python 3.11 и создайте виртуальное окружение:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r docker/requirements.txt
```

Выполните миграции базы данных:
```bash
$ python manage.py migrate
```

### 3. Загрузка тестовых данных
Если необходимо загрузить демонстрационные данные:
```bash
$ python manage.py shell < scripts/demo_2024_data.py
```

### 4. Запуск сервера
```bash
$ python manage.py runserver
```

Сервер будет доступен по адресу: `http://localhost:8000`

## Структура проекта
```
.
├── app
│   ├── config        # Конфигурация Django
│   ├── finances      # Модуль управления финансами
│   ├── main          # Основной модуль приложения
│   ├── organizations # Управление организациями
│   ├── users         # Аутентификация и пользователи
│   ├── scripts       # Скрипты для добавления тестовых данных
│   ├── manage.py     # Управление Django
│   ├── create_admin.py # Скрипт для создания администратора
├── docker
│   ├── Dockerfile      # Dockerfile для контейнеризации
│   ├── docker-compose.dev.yml # Конфигурация Docker Compose
│   ├── entrypoint.sh   # Точка входа для контейнера
│   ├── requirements.txt # Python зависимости
└── inside_repo.sh      # Скрипт выполнения команд в контейнере
```

## Автор
Разработано **A. Golikov**

## Лицензия
MIT License.
