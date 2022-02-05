@REM docker build -t elibrary_api_dev -f Dockerfile.dev .

docker run -it --rm ^
  --name elibrary_api_dev ^
  -v %cd%:/app ^
  -p 8000:8000 ^
  --net host ^
  elibrary_api_dev

@REM python manage.py runserver 0.0.0.0:8000
