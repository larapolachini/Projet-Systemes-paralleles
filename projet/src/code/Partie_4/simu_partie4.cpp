#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <vector>
#include <SDL2/SDL.h>
#include <mpi.h>
#include <fstream>
#include "model.hpp"
#include "display.hpp"

using namespace std::string_literals;
using namespace std::chrono_literals;

struct ParamsType
{
    double length{1.};
    unsigned discretization{20u};
    std::array<double, 2> wind{0., 0.};
    Model::LexicoIndices start{10u, 10u};
};


void analyze_arg( int nargs, char* args[], ParamsType& params )
{
    if (nargs ==0) return;
    std::string key(args[0]);
    if (key == "-l"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour la longueur du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.length = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    auto pos = key.find("--longueur=");
    if (pos < key.size())
    {
        auto subkey = std::string(key,pos+11);
        params.length = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-n"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour le nombre de cases par direction pour la discrétisation du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.discretization = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--number_of_cases=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+18);
        params.discretization = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-w"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la direction du vent !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.wind[0] = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--wind=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+7);
        params.wind[0] = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-s"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la position du foyer initial !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.start.column = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la position du foyer initial" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--start=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+8);
        params.start.column = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }
}

ParamsType parse_arguments( int nargs, char* args[] )
{
    if (nargs == 0) return {};
    if ( (std::string(args[0]) == "--help"s) || (std::string(args[0]) == "-h") )
    {
        std::cout << 
R"RAW(Usage : simulation [option(s)]
  Lance la simulation d'incendie en prenant en compte les [option(s)].
  Les options sont :
    -l, --longueur=LONGUEUR     Définit la taille LONGUEUR (réel en km) du carré représentant la carte de la végétation.
    -n, --number_of_cases=N     Nombre n de cases par direction pour la discrétisation
    -w, --wind=VX,VY            Définit le vecteur vitesse du vent (pas de vent par défaut).
    -s, --start=COL,ROW         Définit les indices I,J de la case où commence l'incendie (milieu de la carte par défaut)
)RAW";
        exit(EXIT_SUCCESS);
    }
    ParamsType params;
    analyze_arg(nargs, args, params);
    return params;
}

bool check_params(ParamsType& params)
{
    bool flag = true;
    if (params.length <= 0)
    {
        std::cerr << "[ERREUR FATALE] La longueur du terrain doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if (params.discretization <= 0)
    {
        std::cerr << "[ERREUR FATALE] Le nombre de cellules par direction doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if ( (params.start.row >= params.discretization) || (params.start.column >= params.discretization) )
    {
        std::cerr << "[ERREUR FATALE] Mauvais indices pour la position initiale du foyer" << std::endl;
        flag = false;
    }
    
    return flag;
}

void display_params(ParamsType const& params)
{
    std::cout << "Parametres définis pour la simulation : \n"
              << "\tTaille du terrain : " << params.length << std::endl 
              << "\tNombre de cellules par direction : " << params.discretization << std::endl 
              << "\tVecteur vitesse : [" << params.wind[0] << ", " << params.wind[1] << "]" << std::endl
              << "\tPosition initiale du foyer (col, ligne) : " << params.start.column << ", " << params.start.row << std::endl;
}

int main(int nargs, char *args[])
{
    MPI_Init(&nargs, &args);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::shared_ptr<Displayer> displayer;
    ParamsType params;

    if (rank == 0)
    {
        params.length = 1.0;
        params.discretization = 20;
        params.wind = {0, 0};
        params.start = {10, 10};

        displayer = Displayer::init_instance(params.discretization, params.discretization);
    }

    MPI_Bcast(&params.length, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Bcast(&params.discretization, 1, MPI_UNSIGNED, 0, MPI_COMM_WORLD);
    MPI_Bcast(params.wind.data(), 2, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Bcast(&params.start.row, 1, MPI_UNSIGNED, 0, MPI_COMM_WORLD);
    MPI_Bcast(&params.start.column, 1, MPI_UNSIGNED, 0, MPI_COMM_WORLD);
    

    int rows_per_proc = params.discretization / size;
    int start_row = rank * rows_per_proc;
    int end_row = (rank == size - 1) ? params.discretization - 1 : (start_row + rows_per_proc - 1);

    Model simu(params.length, params.discretization, params.wind, params.start);

    std::string output_filename = "resultado_mpi_" + std::to_string(size) + ".csv";
    std::ofstream output_file;

    if (rank == 0)
    {
        output_file.open(output_filename);
        if (!output_file.is_open())
        {
            std::cerr << "Erreur lors de l'ouverture du fichier" << output_filename << std::endl;
            perror("Raison du système");
            MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        }

        output_file << "Simulation Parameters:\n";
        output_file << "Length: " << params.length << "\n";
        output_file << "Discretization: " << params.discretization << "\n";
        output_file << "Wind: (" << params.wind[0] << ", " << params.wind[1] << ")\n";
        output_file << "Start Fire Position: (" << params.start.row << ", " << params.start.column << ")\n";
        output_file << "-------------------------------------------\n";
        output_file << "TimeStep;Temps_avancement(ms);Temps_affichage(ms);Temps_total(ms)\n";
    }

    std::vector<std::vector<double>> local_map(rows_per_proc + 2, std::vector<double>(params.discretization));
    bool keep_running = true;
    double start_time = MPI_Wtime();

    while (keep_running)
    {
        double update_time_milli = 0.0;
        {
            auto start_update = std::chrono::high_resolution_clock::now();
            bool local_continue = simu.update();
            auto end_update = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double, std::milli> update_time = end_update - start_update;
            update_time_milli = update_time.count();

            int local_keep_running = local_continue ? 1 : 0;
            int global_keep_running = 0;

            MPI_Allreduce(&local_keep_running, &global_keep_running, 1, MPI_INT, MPI_MIN, MPI_COMM_WORLD);
            keep_running = (global_keep_running == 1);
        }

        if (!keep_running)
            break;

        if (rank > 0)
        {
           
            MPI_Send(local_map[1].data(), params.discretization, MPI_DOUBLE, rank - 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_map[0].data(), params.discretization, MPI_DOUBLE, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

           }

        if (rank < size - 1)
        {
         
            MPI_Send(local_map[rows_per_proc].data(), params.discretization, MPI_DOUBLE, rank + 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_map[rows_per_proc + 1].data(), params.discretization, MPI_DOUBLE, rank + 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      
        }

        double display_time_milli = 0.0;
        if (rank == 0)
        {
            auto start_displayer = std::chrono::high_resolution_clock::now();

            if (displayer)
            {
                displayer->update(simu.vegetal_map(), simu.fire_map());
            }

            auto end_displayer = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double, std::milli> display_time = end_displayer - start_displayer;
            display_time_milli = display_time.count();

            double total_time = update_time_milli + display_time_milli;

            output_file << simu.time_step() << ";" << update_time_milli << ";" << display_time_milli << ";" << total_time << "\n";

            SDL_Event event;
            if (SDL_PollEvent(&event) && event.type == SDL_QUIT)
            {
                keep_running = false;
            }
        }

        int keep = keep_running ? 1 : 0;
        MPI_Bcast(&keep, 1, MPI_INT, 0, MPI_COMM_WORLD);
        keep_running = (keep == 1);

        MPI_Barrier(MPI_COMM_WORLD);
    }

    double end_time = MPI_Wtime();
    double elapsed_time = end_time - start_time;
    double max_time;

    MPI_Reduce(&elapsed_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rank == 0)
    {
        double sequential_time = 3.666;
        double speedup = sequential_time / max_time;
        std::cout << "Speedup: " << speedup << std::endl;
    }

    if (rank == 0)
    {
        output_file << "\nSimulation fermée.\n";
        output_file.close();
    }

    MPI_Finalize();
    SDL_Quit();

    return EXIT_SUCCESS;
}
