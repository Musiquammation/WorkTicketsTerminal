.PHONY: run install clean

VENV = .venv
PYTHON = $(VENV)/bin/python -B
MAIN = src/main.py

run:
	$(PYTHON) $(MAIN)

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -r requirements.txt

clean:
	rm -rf $(VENV)