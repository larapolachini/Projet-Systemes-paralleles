# Variáveis
CXX = g++
CXXFLAGS = -fopenmp
LDFLAGS = -lSDL2

# Arquivos-fonte
PAR_SRC = paralelo.cpp display.cpp model.cpp
SEQ_SRC = simulation.cpp display.cpp model2.cpp

# Executáveis
PAR_EXEC = par
SEQ_EXEC = seq

# Alvo padrão
all: $(PAR_EXEC) $(SEQ_EXEC) run

# Compila versão paralela
$(PAR_EXEC): $(PAR_SRC)
	$(CXX) $(CXXFLAGS) $(PAR_SRC) $(LDFLAGS) -o $(PAR_EXEC)

# Compila versão sequencial
$(SEQ_EXEC): $(SEQ_SRC)
	$(CXX) $(SEQ_SRC) $(LDFLAGS) -o $(SEQ_EXEC)

# Limpeza dos binários
clean:
	rm -f $(PAR_EXEC) $(SEQ_EXEC)
