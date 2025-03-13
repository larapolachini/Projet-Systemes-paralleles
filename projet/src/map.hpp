#ifndef MAP_HPP
#define MAP_HPP

#include <string>
#include <vector>
#include <cstdint>

// Funções para salvar e comparar mapas
void save_map_to_file(const std::string& filename, const std::vector<uint8_t>& map);
bool compare_map_with_file(const std::string& filename, const std::vector<uint8_t>& map);

#endif
