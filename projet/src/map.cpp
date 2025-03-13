#include "map.hpp"
#include <fstream>
#include <iostream>
#include <numeric>

// Salva o mapa inteiro num arquivo (cada valor separado por espaço)
void save_map_to_file(const std::string& filename, const std::vector<uint8_t>& map) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo para salvar: " << filename << std::endl;
        return;
    }

    for (const auto& val : map) {
        file << int(val) << " ";
    }
    file << std::endl;
    file.close();

    std::cout << "Mapa salvo em: " << filename << std::endl;
}

// Compara um mapa atual com o salvo em arquivo
bool compare_map_with_file(const std::string& filename, const std::vector<uint8_t>& map) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo para comparação: " << filename << std::endl;
        return false;
    }

    int val;
    size_t i = 0;
    bool identical = true;

    while (file >> val) {
        if (i >= map.size()) {
            std::cerr << "Arquivo maior que o mapa atual!" << std::endl;
            identical = false;
            break;
        }

        if (map[i] != val) {
            std::cerr << "Diferença encontrada no índice " << i
                      << ": paralelo=" << int(map[i])
                      << " vs sequencial=" << val << std::endl;
            identical = false;
        }
        ++i;
    }

    if (i < map.size()) {
        std::cerr << "Arquivo menor que o mapa atual!" << std::endl;
        identical = false;
    }

    if (identical) {
        std::cout << "[OK] Mapa igual ao arquivo: " << filename << std::endl;
    } else {
        std::cout << "[ERRO] Mapa DIFERENTE de: " << filename << std::endl;
    }

    return identical;
}
