.PHONY: setup split train-xgb train-xgb-tune api ui test

VENV    = .venv
PYTHON  = $(VENV)/bin/python
PIP     = $(VENV)/bin/pip

setup:
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

split:
	$(PYTHON) -m src.data_prep

train-xgb:
	$(PYTHON) -m src.train_xgb

train-xgb-tune:
	$(PYTHON) -m src.train_xgb --tune

api:
	$(VENV)/bin/uvicorn backend.app:app --reload --port 8000

ui:
	$(VENV)/bin/streamlit run frontend/app.py --server.port 8501

test:
	$(VENV)/bin/pytest tests/ -v
