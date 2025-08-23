default:
	./dev_launch.sh

test:
	uv run manage.py test

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

runserver:
	uv run manage.py runserver