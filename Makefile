default:
	./dev_launch.sh

tests:
	source .venv/bin/activate && python3  manage.py test