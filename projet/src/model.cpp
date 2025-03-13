#include <stdexcept>
#include <cmath>
#include <iostream>
#include "model.hpp"
#include "algorithm"


namespace
{
    double pseudo_random( std::size_t index, std::size_t time_step,std::size_t seed = 42)
    {
        std::uint_fast32_t xi = std::uint_fast32_t(index*(time_step+1)+ seed);
        std::uint_fast32_t r  = (48271*xi)%2147483647;
        return r/2147483646.;
    }

    double log_factor( std::uint8_t value )
    {
        return std::log(1.+value)/std::log(256);
    }
}

Model::Model( double t_length, unsigned t_discretization, std::array<double,2> t_wind,
              LexicoIndices t_start_fire_position, double t_max_wind )
    :   m_length(t_length),
        m_distance(-1),
        m_geometry(t_discretization),
        m_wind(t_wind),
        m_wind_speed(std::sqrt(t_wind[0]*t_wind[0] + t_wind[1]*t_wind[1])),
        m_max_wind(t_max_wind),
        m_vegetation_map(t_discretization*t_discretization, 255u),
        m_fire_map(t_discretization*t_discretization, 0u),
        m_time_step(0u)
{
    if (t_discretization == 0)
    {
        throw std::range_error("Le nombre de cases par direction doit être plus grand que zéro.");
    }
    m_distance = m_length/double(m_geometry);
    auto index = get_index_from_lexicographic_indices(t_start_fire_position);
    m_fire_map[index] = 255u;
    m_fire_front[index] = 255u;

    constexpr double alpha0 = 4.52790762e-01;
    constexpr double alpha1 = 9.58264437e-04;
    constexpr double alpha2 = 3.61499382e-05;

    if (m_wind_speed < t_max_wind)
        p1 = alpha0 + alpha1*m_wind_speed + alpha2*(m_wind_speed*m_wind_speed);
    else 
        p1 = alpha0 + alpha1*t_max_wind + alpha2*(t_max_wind*t_max_wind);
    p2 = 0.3;

    if (m_wind[0] > 0)
    {
        alphaEastWest = std::abs(m_wind[0]/t_max_wind)+1;
        alphaWestEast = 1.-std::abs(m_wind[0]/t_max_wind);    
    }
    else
    {
        alphaWestEast = std::abs(m_wind[0]/t_max_wind)+1;
        alphaEastWest = 1. - std::abs(m_wind[0]/t_max_wind);
    }

    if (m_wind[1] > 0)
    {
        alphaSouthNorth = std::abs(m_wind[1]/t_max_wind) + 1;
        alphaNorthSouth = 1. - std::abs(m_wind[1]/t_max_wind);
    }
    else
    {
        alphaNorthSouth = std::abs(m_wind[1]/t_max_wind) + 1;
        alphaSouthNorth = 1. - std::abs(m_wind[1]/t_max_wind);
    }
}
bool Model::update() {
    auto next_front = m_fire_front;

    // Lista de células em chamas (ordem determinística)
    std::vector<std::size_t> fire_indices;
    for (const auto& f : m_fire_front) {
        fire_indices.push_back(f.first);
    }

    // Passo 1: Propagação (gerar novos focos de incêndio)
    std::unordered_map<std::size_t, uint8_t> propagated_cells;

    #pragma omp parallel
    {
        std::unordered_map<std::size_t, uint8_t> local_propagation;

        #pragma omp for schedule(static)
        for (size_t i = 0; i < fire_indices.size(); i++) {
            std::size_t f_first = fire_indices[i];
            uint8_t f_second = m_fire_front.at(f_first);

            LexicoIndices coord = get_lexicographic_from_index(f_first);
            double power = log_factor(f_second);

            auto propagate = [&](std::size_t neighbor_idx, double alpha_dir, std::size_t tirage_key) {
                double tirage = pseudo_random(tirage_key, m_time_step);
                double green_power = m_vegetation_map[neighbor_idx];
                double correction = power * log_factor(green_power);

                if (tirage < alpha_dir * p1 * correction) {
                    local_propagation[neighbor_idx] = 255;
                }
            };

            if (coord.row < m_geometry - 1)
                propagate(f_first + m_geometry, alphaSouthNorth, f_first + m_time_step);

            if (coord.row > 0)
                propagate(f_first - m_geometry, alphaNorthSouth, f_first * 13427 + m_time_step);

            if (coord.column < m_geometry - 1)
                propagate(f_first + 1, alphaEastWest, f_first * 13427 * 13427 + m_time_step);

            if (coord.column > 0)
                propagate(f_first - 1, alphaWestEast, f_first * 13427 * 13427 * 13427 + m_time_step);
        }

        // Merge seguro dos novos incêndios
        #pragma omp critical
        {
            for (const auto& pair : local_propagation) {
                propagated_cells[pair.first] = 255;
            }
        }
    }

    // Passo 2: Atualização de intensidade (enfraquecimento + propagação)
    std::unordered_map<std::size_t, uint8_t> updated_front;

    for (const auto& f : m_fire_front) {
        std::size_t idx = f.first;
        uint8_t intensity = f.second;

        // Enfraquece o fogo
        uint8_t new_intensity = intensity;

        if (intensity == 255) {
            double tirage = pseudo_random(idx * 52513 + m_time_step, m_time_step);
            if (tirage < p2) {
                new_intensity = intensity >> 1;
            }
        } else {
            new_intensity = intensity >> 1;
        }

        if (new_intensity > 0) {
            updated_front[idx] = new_intensity;
        }
    }

    // Passo 3: Adiciona as novas células propagadas
    for (const auto& p : propagated_cells) {
        updated_front[p.first] = 255;  // sempre 255 ao propagar
    }

    // Passo 4: Atualiza o m_fire_map de forma ordenada (para consistência)
    std::vector<std::size_t> ordered_keys;
    for (const auto& p : updated_front) {
        ordered_keys.push_back(p.first);
    }

    std::sort(ordered_keys.begin(), ordered_keys.end());

    for (const auto& idx : ordered_keys) {
        uint8_t value = updated_front[idx];

        m_fire_map[idx] = value;

        if (value > 0) {
            next_front[idx] = value;
        } else {
            next_front.erase(idx);
        }
    }

    // Passo 5: Atualiza a vegetação nas células com fogo
    #pragma omp parallel for
    for (size_t i = 0; i < ordered_keys.size(); i++) {
        std::size_t idx = ordered_keys[i];
        if (m_fire_map[idx] > 0 && m_vegetation_map[idx] > 0) {
            m_vegetation_map[idx] -= 1;
        }
    }

    m_fire_front = next_front;
    m_time_step++;

    return !m_fire_front.empty();
}

std::size_t   
Model::get_index_from_lexicographic_indices( LexicoIndices t_lexico_indices  ) const
{
    return t_lexico_indices.row*this->geometry() + t_lexico_indices.column;
}
// --------------------------------------------------------------------------------------------------------------------
auto 
Model::get_lexicographic_from_index( std::size_t t_global_index ) const -> LexicoIndices
{
    LexicoIndices ind_coords;
    ind_coords.row    = t_global_index/this->geometry();
    ind_coords.column = t_global_index%this->geometry();
    return ind_coords;
}