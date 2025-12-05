default: runserver

test:
	uv run manage.py test

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

runserver:
	./dev_launch.sh

generate-demo-data:
	 uv run manage.py generate_demo_data

generateproto:
	uv run manage.py generateproto

grpc-devserver:
	uv run manage.py grpcrunaioserver --dev

install:
	uv sync
