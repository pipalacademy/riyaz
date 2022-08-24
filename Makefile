.PHONY: runlocal test serve-cov

runlocal:
	FLASK_APP=riyaz.app:app FLASK_DEBUG=true flask run

test:
	pytest --cov=riyaz --cov-report html tests/

serve-cov:
	python -m http.server --directory htmlcov/
