test:
	cd bot && PYTHONPATH=./ python -m pytest tests/
	cd ..

.PHONY: test
