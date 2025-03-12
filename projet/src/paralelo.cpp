#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <SDL2/SDL.h>
#include <omp.h>
#include "model.hpp"
#include "display.hpp"
#include <fstream>  // Adiciona a biblioteca para arquivos



using namespace std::string_literals;
using namespace std::chrono_literals;

struct ParamsType
{
    double length{1.};
    unsigned discretization{20u};
    std::array<double,2> wind{0.,0.};
    Model::LexicoIndices start{10u,10u};
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

int main(int nargs, char* args[])
{
    auto params = parse_arguments(nargs - 1, &args[1]);
    display_params(params);
    if (!check_params(params)) return EXIT_FAILURE;

    auto displayer = Displayer::init_instance(params.discretization, params.discretization);
    auto simu = Model(params.length, params.discretization, params.wind, params.start);
    int num_threads = omp_get_max_threads();

    std::string output_filename = "simulation_" + std::to_string(num_threads) + "threads.txt";
    std::ofstream output_file(output_filename);
    if (!output_file.is_open())
    {
        std::cerr << "Erro ao abrir o arquivo para escrita!" << std::endl;
        
        return EXIT_FAILURE;
    }

    output_file << "Simulation Parameters:\n";
    output_file << "Length: " << params.length << "\n";
    output_file << "Discretization: " << params.discretization << "\n";
    output_file << "Wind: (" << params.wind[0] << ", " << params.wind[1] << ")\n";
    output_file << "Start Fire Position: (" << params.start.row << ", " << params.start.column << ")\n";
    output_file << "-------------------------------------------\n";
    output_file << "TimeStep\tUpdateTime(ms)\tDisplayTime(ms)\tTotalTime(ms)\n";

    SDL_Event event;
    bool keep_running = true;
    while (keep_running)
    {
        // Cronometragem total
        auto start_total = std::chrono::high_resolution_clock::now();

        // Atualização do modelo
        auto start_update = std::chrono::high_resolution_clock::now();
        keep_running = simu.update();
        auto end_update = std::chrono::high_resolution_clock::now();

        if (!keep_running) {
            std::cout << "Simulação finalizada antecipadamente no time_step " << simu.time_step() << std::endl;
            break;
        }

        std::chrono::duration<double, std::milli> update_time = end_update - start_update;

        // Exibição periódica a cada 32 passos
        if ((simu.time_step() & 31) == 0)
        {
            std::cout << "Time step " << simu.time_step() << "\n===============" << std::endl;
            output_file << "\nTime step " << simu.time_step() << "\n===============" << std::endl;
        }

        // Atualiza a tela
        auto vegetal = simu.vegetal_map();
        auto fire = simu.fire_map();

        if (vegetal.empty() || fire.empty()) {
            std::cerr << "Mapas vazios! Encerrando simulação." << std::endl;
            break;
        }

        auto start_displayer = std::chrono::high_resolution_clock::now();
        displayer->update(vegetal, fire);
        auto end_displayer = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double, std::milli> display_time = end_displayer - start_displayer;

        // Evento SDL para fechar janela
        if (SDL_PollEvent(&event) && event.type == SDL_QUIT)
            break;

        auto end_total = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> total_time = end_total - start_total;

        std::this_thread::sleep_for(0.1s);

        std::cout << "Update Time: " << update_time.count() << " ms, ";
        std::cout << "Display Time: " << display_time.count() << " ms, ";
        std::cout << "Total Time: " << total_time.count() << " ms\n";

        output_file << simu.time_step() << "\t"
                    << update_time.count() << "\t"
                    << display_time.count() << "\t"
                    << total_time.count() << "\n";

    }

    output_file << "\nSimulation Ended.\n";
    output_file.close();
    return EXIT_SUCCESS;
}