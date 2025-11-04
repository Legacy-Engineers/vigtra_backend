default: runserver

test:
	uv run manage.py test

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

runserver:
	./dev_launch.sh

generateproto:
	uv run manage.py generateproto

grpc-devserver:
	uv run manage.py grpcrunaioserver --dev

install:
	uv sync
