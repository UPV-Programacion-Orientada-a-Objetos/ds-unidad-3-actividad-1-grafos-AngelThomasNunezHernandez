#ifndef GRAPHCORE_H
#define GRAPHCORE_H

#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <queue>
#include <unordered_set>
#include <unordered_map>
#include <cstdio>

class GrafoBase {
public:
    virtual void cargarDatos(std::string filename) = 0;
    virtual std::vector<long long> bfs(long long startNodeID, int maxDepth) = 0;
    virtual long long obtenerNodoCritico() = 0;
    virtual ~GrafoBase() {}
};

class GrafoDisperso : public GrafoBase {
private:
    int num_nodes;
    int num_edges;
    
    std::vector<int> row_ptr;
    std::vector<int> col_ind;

    std::unordered_map<long long, int> raw_to_internal; 

    std::vector<long long> internal_to_raw; 

public:
    GrafoDisperso() : num_nodes(0), num_edges(0) {}

    void cargarDatos(std::string filename) override {
        raw_to_internal.clear();
        internal_to_raw.clear();
        row_ptr.clear();
        col_ind.clear();

        std::cout << "[C++ Core] Optimizacion activada: Lectura rapida y Mapeo de IDs." << std::endl;
        
        FILE* file = fopen(filename.c_str(), "r");
        if (!file) throw std::runtime_error("No se pudo abrir el archivo");

        std::vector<std::pair<int, int>> edges_temp;
        
        edges_temp.reserve(1000000); 

        long long u_raw, v_raw;
        int next_internal_id = 0;

        while (fscanf(file, "%lld %lld", &u_raw, &v_raw) == 2) {
            if (raw_to_internal.find(u_raw) == raw_to_internal.end()) {
                raw_to_internal[u_raw] = next_internal_id;
                internal_to_raw.push_back(u_raw);
                next_internal_id++;
            }
            if (raw_to_internal.find(v_raw) == raw_to_internal.end()) {
                raw_to_internal[v_raw] = next_internal_id;
                internal_to_raw.push_back(v_raw);
                next_internal_id++;
            }

            edges_temp.push_back({raw_to_internal[u_raw], raw_to_internal[v_raw]});
        }
        fclose(file);

        num_nodes = next_internal_id;
        num_edges = edges_temp.size();

        std::sort(edges_temp.begin(), edges_temp.end());

        row_ptr.assign(num_nodes + 1, 0);
        col_ind.reserve(num_edges);

        std::vector<int> degree_count(num_nodes, 0);
        for (const auto& edge : edges_temp) {
            degree_count[edge.first]++;
        }

        int current_ptr = 0;
        for (int i = 0; i < num_nodes; ++i) {
            row_ptr[i] = current_ptr;
            current_ptr += degree_count[i];
        }
        row_ptr[num_nodes] = current_ptr;

        for (const auto& edge : edges_temp) {
            col_ind.push_back(edge.second);
        }

        std::vector<std::pair<int, int>>().swap(edges_temp);

        std::cout << "[C++ Core] Grafo Optimizado. Nodos Reales: " << num_nodes << " | Aristas: " << num_edges << std::endl;
    }

    std::vector<long long> bfs(long long startNodeID, int maxDepth) override {
        std::vector<long long> result_edges;
        
        if (raw_to_internal.find(startNodeID) == raw_to_internal.end()) {
            return result_edges;
        }

        int startInternal = raw_to_internal[startNodeID];
        
        std::queue<std::pair<int, int>> q;
        std::vector<bool> visited(num_nodes, false);

        q.push({startInternal, 0});
        visited[startInternal] = true;

        int edges_count_limit = 2000;

        while (!q.empty()) {
            int u = q.front().first;
            int depth = q.front().second;
            q.pop();

            if (depth >= maxDepth) continue;
            if (result_edges.size() >= edges_count_limit * 2) break;

            for (int i = row_ptr[u]; i < row_ptr[u+1]; ++i) {
                int v = col_ind[i];
                
                result_edges.push_back(internal_to_raw[u]);
                result_edges.push_back(internal_to_raw[v]);

                if (!visited[v]) {
                    visited[v] = true;
                    q.push({v, depth + 1});
                }
            }
        }
        return result_edges;
    }

    long long obtenerNodoCritico() override {
        int max_degree = -1;
        int internal_node_crit = -1;

        for (int i = 0; i < num_nodes; ++i) {
            int degree = row_ptr[i+1] - row_ptr[i];
            if (degree > max_degree) {
                max_degree = degree;
                internal_node_crit = i;
            }
        }
        if (internal_node_crit == -1) return -1;
        return internal_to_raw[internal_node_crit];
    }
};

#endif