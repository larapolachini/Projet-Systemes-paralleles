#include "map.hpp"
#include <fstream>
#include <iostream>
#include <numeric>

// Enregistrer la carte entière dans un fichier (chaque valeur séparée par un espace)
void save_map_to_file(const std::string& filename, const std::vector<uint8_t>& map) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erreur lors de l'ouverture du fichier à enregistrer: " << filename << std::endl;
        return;
    }

    for (const auto& val : map) {
        file << int(val) << " ";
    }
    file << std::endl;
    file.close();

    std::cout << "Carte enregistrée dans : " << filename << std::endl;
}

// Compare une carte actuelle avec celle enregistrée dans le fichier
bool compare_map_with_file(const std::string& filename, const std::vector<uint8_t>& map) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erreur lors de l'ouverture du fichier pour comparaison : " << filename << std::endl;
        return false;
    }

    int val;
    size_t i = 0;
    bool identical = true;

    while (file >> val) {
        if (i >= map.size()) {
            std::cerr << "Fichier plus grand que la carte actuelle !" << std::endl;
            identical = false;
            break;
        }

        if (map[i] != val) {
            std::cerr << "Différence trouvée dans l'index " << i
                      << ": parallèle=" << int(map[i])
                      << " vs séquentiel=" << val << std::endl;
            identical = false;
        }
        ++i;
    }

    if (i < map.size()) {
        std::cerr << "Fichier plus petit que la carte actuelle !" << std::endl;
        identical = false;
    }

    if (identical) {
        std::cout << "[OK] Carte identique au fichier: " << filename << std::endl;
    } else {
        std::cout << "[ERRO] DIFFÉRENTE carte de: " << filename << std::endl;
    }

    return identical;
}
