.PHONY: runlocal

runlocal:
	FLASK_APP=riyaz.app:app FLASK_DEBUG=true flask run
