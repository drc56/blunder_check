FROM ubuntu:20.04

RUN apt-get update && apt-get install -yq make python3 python3-pip wget 
RUN curl -sL https://rpm.nodesource.com/setup_18.x | bash -
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y  nodejs npm

WORKDIR /bc

# Setup Stockfish
RUN wget https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_15.tar.gz
RUN tar -xf sf_15.tar.gz
RUN cd Stockfish-sf_15/src && make build ARCH=x86-64-modern
