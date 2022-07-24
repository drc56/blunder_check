

sfdocker:
	docker build -t sfdocker -f evaluator/Stockfish.Dockerfile .

evaldocker: sfdocker
	docker build -t bcevaluator evaluator/.

run: evaldocker
	docker run -p 8000:8000 bcevaluator

.PHONY: run