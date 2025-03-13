#include <iostream>
#include <fstream>
#include <string>
#include <array>
#include "model.hpp"

// Atalho para LexicoIndices
using LexicoIndices = Model::LexicoIndices;

void save_map(const std::string &filename, const std::vector<uint8_t> &map, unsigned geometry)
{
    std::ofstream out(filename);
    if (!out.is_open())
    {
        std::cerr << "[ERRO] Não foi possível abrir o arquivo " << filename << std::endl;
        return;
    }

    for (unsigned row = 0; row < geometry; ++row)
    {
        for (unsigned col = 0; col < geometry; ++col)
        {
            std::size_t idx = row * geometry + col;
            out << static_cast<int>(map[idx]);
            if (col < geometry - 1)
                out << " ";
        }
        out << "\n";
    }

    out.close();
    std::cout << "[INFO] Mapa salvo em: " << filename << std::endl;
}

int main()
{
    double length = 100.0;
    unsigned discretization = 20;
    std::array<double, 2> wind = {5.0, 0.0};
    LexicoIndices start_fire = {discretization / 2, discretization / 2};
    double max_wind = 20.0;

    Model simulation(length, discretization, wind, start_fire, max_wind);

    int max_steps = 500;
    int steps = 0;

    while (simulation.update() && steps < max_steps)
    {
        ++steps;
        if (steps % 50 == 0)
            std::cout << "Passo " << steps << " concluído." << std::endl;
    }

    std::cout << "Simulação concluída em " << steps << " passos." << std::endl;

    save_map("fire_map_seq2.txt", simulation.fire_map(), simulation.geometry());
    save_map("vegetation_map_seq2.txt", simulation.vegetation_map(), simulation.geometry());

    return 0;
}
