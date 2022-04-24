FROM ubuntu:20.04

WORKDIR /bc

RUN apt-get update && apt-get install -y make python3 python3-pip wget

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000

COPY src /bc/src

# Setup Stockfish
RUN wget https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_15.tar.gz
RUN tar -xf sf_15.tar.gz
RUN cd Stockfish-sf_15/src && make build ARCH=x86-64-modern

CMD [ "python3", "src/stockfish_evaluator.py" ]