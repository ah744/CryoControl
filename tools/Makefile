# Makefile
BIN = ./bin
SOURCE = ./source

all : $(BIN)/linker $(BIN)/cachesim $(BIN)/moduleextraction

$(BIN)/linker : $(SOURCE)/Linker.cpp
	mkdir -p bin
	g++ -std=c++11 $(SOURCE)/Linker.cpp -o $(BIN)/linker 
$(BIN)/cachesim : $(SOURCE)/CacheSim.cpp
	mkdir -p bin
	g++ -std=c++11 $(SOURCE)/CacheSim.cpp -o $(BIN)/cachesim
$(BIN)/moduleextraction : $(SOURCE)/ModuleExtraction.cpp
	mkdir -p bin
	g++ -std=c++11 $(SOURCE)/ModuleExtraction.cpp -o $(BIN)/moduleextraction 
