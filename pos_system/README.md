# Point of Sale (POS) System

This is a Django-based Point of Sale (POS) system designed to manage sales transactions efficiently.

## Project Structure

```
pos_system/
├── pos_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── pos/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── manage.py
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd pos_system
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install django
   ```

4. **Run migrations:**
   ```
   python manage.py migrate
   ```

5. **Start the development server:**
   ```
   python manage.py runserver
   ```

## Usage

- Access the application at `http://127.0.0.1:8000/`.
- Use the Django admin interface to manage products, sales, and other data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.