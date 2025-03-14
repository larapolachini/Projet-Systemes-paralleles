# Makefile

CXX = mpic++
CXXFLAGS = -fopenmp -Wall -std=c++17
LDFLAGS = -lSDL2

TARGET = simu_MPI
SOURCES = simu_MPI.cpp display.cpp model.cpp

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

# Regra para executar todas as combinações
run_all:
	@for mpi in 1 2 4; do \
		for t in 1 2 4 8 ; do \
			echo "Executando com MPI size $$mpi e OMP_NUM_THREADS $$t"; \
			export OMP_NUM_THREADS=$$t; \
			mpirun -np $$mpi ./$(TARGET); \
		done; \
	done

clean:
	rm -f $(TARGET)
