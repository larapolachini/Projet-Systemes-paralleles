# Compiler and flags
CXX = mpic++
CXXFLAGS = -fopenmp -Wall -std=c++17 -O2
LDFLAGS = -lSDL2

# Target and sources
TARGET = partie3
SOURCES = simu_MPI_par.cpp display.cpp model.cpp

# Diretório de resultados (opcional)

# Regra padrão
all: $(TARGET)

# Como compilar o binário
$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

# Regra para executar todas as combinações
run_all: all
	@for mpi in 1 2 4; do \
		for t in 1 2 4 8; do \
			echo "Executando com MPI size $$mpi e OMP_NUM_THREADS=$$t"; \
			export OMP_NUM_THREADS=$$t; \
			mpirun --bind-to none -np $$mpi ./$(TARGET) -n 100; \
		done; \
	done

# Limpa binário e resultados
clean:
	rm -f $(TARGET)
	rm -rf $(RESULTS_DIR)
