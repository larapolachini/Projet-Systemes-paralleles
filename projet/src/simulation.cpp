#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <SDL2/SDL.h>

#include "model.hpp"
#include "display.hpp"
#include <fstream> 
#include <vector>
#include "map.hpp"



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
    SDL_Event event;
    bool keep_running = true;
    int step_count = 0;
    int max_steps = 100;

    double temps_total_avancement = 0.0;
    double temps_total_affichage = 0.0;
    unsigned long nb_iterations = 0;
    std::vector<double> temps_avancement_par_iteration;
    std::vector<double> temps_affichage_par_iteration;
    std::vector<int> time_steps;

    
    while (simu.update() && nb_iterations < 1001)
    {
        //auto start_total = std::chrono::high_resolution_clock::now();

        auto start_update = std::chrono::high_resolution_clock::now();
        bool keep_running = simu.update();  // Só chama uma vez aqui!
        auto end_update = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double, std::milli> update_time = end_update - start_update;
        temps_total_avancement += update_time.count();

        auto start_displayer = std::chrono::high_resolution_clock::now();
        displayer->update(simu.vegetal_map(), simu.fire_map());
        auto end_displayer = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double, std::milli> display_time = end_displayer - start_displayer;
        temps_total_affichage += display_time.count();

        int current_timestep = simu.time_step();
        time_steps.push_back(current_timestep);

        nb_iterations++;


        temps_avancement_par_iteration.push_back(update_time.count());
        temps_affichage_par_iteration.push_back(display_time.count());
        std::vector<int> time_steps;





        if ((simu.time_step() & 31) == 0)
        {
            std::cout << "Time step " << simu.time_step() << "\n===============" << std::endl;
             // Affichage des moyennes à l'instant T
            std::cout << "Moyenne avancement : " 
                << (temps_total_avancement / nb_iterations) * 1000.0 
                << " ms" << std::endl;
            std::cout << "Moyenne affichage : " 
                << (temps_total_affichage / nb_iterations) * 1000.0 
                << " ms" << std::endl;
        }

        if (SDL_PollEvent(&event) && event.type == SDL_QUIT)
            break;

        std::this_thread::sleep_for(0.1s);

    }


    std::ofstream fichier_csv("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps.csv");

    if (fichier_csv.is_open())
    {
        // En-têtes
        fichier_csv << "Iteration;TimeStep;Temps_avancement(ms);Temps_affichage(ms);Temps_total(ms)\n";
    
        for (size_t i = 0; i < temps_avancement_par_iteration.size(); ++i)
        {
            double total = temps_avancement_par_iteration[i] + temps_affichage_par_iteration[i];
            fichier_csv << i << "; "
                        << time_steps[i] << "; "
                        << temps_avancement_par_iteration[i] << "; "
                        << temps_affichage_par_iteration[i] << "; "
                        << total << "\n";
        }
    
        fichier_csv.close();
        std::cout << "Fichier CSV 'resultats_temps.csv' généré avec succès !\n";
    }
    else
    {
        std::cerr << "Erreur à l'ouverture du fichier CSV !" << std::endl;
    }


    std::cout << "Simulation terminée !" << std::endl;
    std::cout << "Nombre d'iterations : " << nb_iterations << std::endl;

    std::cout << "Temps moyen d'avancement : " 
              << (temps_total_avancement / nb_iterations) * 1000.0 
              << " ms" << std::endl;

    std::cout << "Temps moyen d'affichage : " 
              << (temps_total_affichage / nb_iterations) * 1000.0 
              << " ms" << std::endl;

    std::cout << "Temps moyen total par pas de temps : " 
              << ((temps_total_avancement + temps_total_affichage) / nb_iterations) * 1000.0 
              << " ms" << std::endl;





    
    return EXIT_SUCCESS;
}

