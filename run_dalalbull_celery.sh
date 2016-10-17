cd ExcelGames
python manage.py celery -A ExcelGames worker --concurrency=1 -B
