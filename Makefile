default: runserver

test:
	uv run manage.py test

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

runserver:
	./dev_launch.sh

install:
	uv sync
