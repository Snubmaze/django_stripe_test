# Django Stripe App

Простое Django приложение для работы с товарами и обработки платежей через Stripe. Использует PostgreSQL в Docker.

## Подготовка

### 1. Получите Stripe API ключи

1. Зарегистрируйтесь или войдите на [Stripe Dashboard](https://dashboard.stripe.com)
2. Перейдите в раздел [API keys](https://dashboard.stripe.com/apikeys)
3. Скопируйте **Secret Key** и **Publishable Key** из тестового режима
4. Вставьте их в файл `.env.example`:

```env
STRIPE_SECRET_KEY=sk_test...
STRIPE_PUBLISHABLE_KEY=pk_test...
```

## Быстрый запуск

```bash
chmod +x run.sh
./run.sh
```

Скрипт автоматически:
- Создаст `.env` из `.env.example` (если не существует)
- Поднимет Docker контейнеры с PostgreSQL и Django
- Запустит миграции
- Создаст администратора
- Инициализирует тестовые данные


## Доступ

После запуска приложение доступно по адресу:

- **Приложение**: http://localhost:8000
- **Админ панель**: http://localhost:8000/admin
- **Учетные данные админа** (по умолчанию): 
  - Username: `admin`
  - Password: `admin`

## Структура проекта

```
stripe_app/
├── items/                          # Django приложение
│   ├── management/commands/
│   │   ├── create_admin.py        # Создание администратора
│   │   └── initdata.py            # Инициализация тестовых данных
│   ├── templates/items/
│   │   ├── item.html              # Страница товара
│   │   └── order.html             # Страница корзины
│   ├── models.py                  # Модели (Item, Order, OrderItem, etc)
│   ├── views.py                   # Обработчики запросов
│   └── utils.py                   # Утилиты для работы со Stripe
├── stripe_app/
│   ├── settings.py                # Конфигурация Django
│   ├── urls.py                    # URL маршруты
│   └── wsgi.py
├── docker-compose.yaml            # Docker Compose конфигурация
├── Dockerfile                      # Docker образ приложения
├── entrypoint.sh                  # Скрипт инициализации контейнера
├── run.sh                         # Bash скрипт для быстрого запуска
├── .env.example                   # Пример переменных окружения
└── requirements.txt               # Python зависимости
```

## Структура базы данных

### Модель Item
Товары для продажи

| Поле | Тип | Описание |
|---|---|---|
| id | Integer | Primary key |
| name | String(60) | Название товара |
| description | Text | Описание товара |
| price | Integer | Цена в центах (например 1000 = $10.00) |

### Модель Order
Заказ (корзина)

| Поле | Тип | Описание |
|---|---|---|
| id | Integer | Primary key |
| created_at | DateTime | Дата создания |
| is_paid | Boolean | Оплачен ли заказ |
| discount | ForeignKey | Скидка (опционально) |
| tax | ForeignKey | Налог (опционально) |

### Модель OrderItem
Товар в заказе (связь many-to-many между Order и Item)

| Поле | Тип | Описание |
|---|---|---|
| id | Integer | Primary key |
| order | ForeignKey | Ссылка на Order |
| item | ForeignKey | Ссылка на Item |
| quantity | Integer | Количество товара |

### Модель Discount
Скидка на заказ

| Поле | Тип | Описание |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Название скидки |
| discount_type | String(20) | Тип: percentage или fixed |
| value | Integer | Размер скидки (% или центы) |
| stripe_coupon_id | String(100) | ID купона в Stripe |
| is_active | Boolean | Активна ли скидка |
| created_at | DateTime | Дата создания |

### Модель Tax
Налог на заказ

| Поле | Тип | Описание |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Название налога |
| percentage | Decimal(5,2) | Процент налога |
| stripe_tax_rate_id | String(100) | ID налога в Stripe |
| is_active | Boolean | Активен ли налог |
| created_at | DateTime | Дата создания |


## API endpoints

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/items/<id>/` | Страница товара с кнопкой покупки |
| POST | `/buy/<id>/` | Создать Stripe Session для одного товара |
| POST | `/add-to-cart/<id>/` | Добавить товар в корзину |
| GET | `/cart/` | Страница корзины |
| POST | `/buy-order/<id>/` | Создать Stripe Session для заказа |
| POST | `/cart/change/<order_id>/<item_id>/` | Изменить количество товара |
| POST | `/cart/delete/<order_id>/<item_id>/` | Удалить товар из корзины |

## Остановка приложения

```bash
docker-compose down
```

### Очистка (включая БД)

```bash
docker-compose down -v
```

## Технологии

- **Django 4.x** - Python веб-фреймворк
- **PostgreSQL 15** - база данных
- **Docker & Docker Compose** - контейнеризация
- **Stripe API** - обработка платежей
- **Bootstrap-подобный CSS** - стилизация

## Тестирование платежей

Используйте тестовые карты Stripe:
- **Успешный платеж**: 4242 4242 4242 4242
- **Отклоненный платеж**: 4000 0000 0000 0002
- Дата: любая будущая дата (например 12/25)
- CVC: любые 3 цифры (например 123)

Полный список тестовых карт: https://stripe.com/docs/testing

## Источники Stripe ключей

**Получение тестовых ключей:**
1. Перейдите на https://dashboard.stripe.com/apikeys
2. Убедитесь, что включен **тестовый режим** (справа вверху переключатель)
3. Скопируйте ключи:
   - **Publishable key** (начинается с `pk_test_`)
   - **Secret key** (начинается с `sk_test_`)
4. Вставьте их в `.env.example`