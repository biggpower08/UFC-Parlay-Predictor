# UFC Predictor

Modular MMA fight analysis: stats, rankings, Elo, sklearn predictions, and user feedback loop.

## Run

```bash
cd mma-ai
pip install -r requirements.txt
python -m ufc_predictor.training.train    # first-time model
python -m ufc_predictor.main              # interactive breakdown + feedback
python -m ufc_predictor.training.retrain  # retrain with feedback
python -m unittest discover -s ufc_predictor/tests -v
```

## Layout

See project root `ufc_predictor/` tree in repo.

## Future: agentic data collection

Planned flow: missing fighter → web search → scrape → validate → update DB → predict.
Placeholder: `models/neural_net/future_model.py`, future `agents/` modules.
