FROM sfdocker

WORKDIR /bc

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN npm install @chrisoakman/chessboardjs

EXPOSE 8000

COPY src /bc/src

CMD [ "python3", "src/stockfish_evaluator.py" ]