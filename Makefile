.PHONY: run fmt lint clean

run:
	uvicorn app.main:app --reload --port 8080

fmt:
	ruff format .

lint:
	ruff check .

clean:
	find app -name "__pycache__" -type d -exec rm -rf {} +; \
	find app -name "*.pyc" -delete

