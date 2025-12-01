# distutils: language = c++

from neuronet_lib cimport GrafoDisperso
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef class NeuroNetEngine:
    cdef GrafoDisperso* c_grafo

    def __cinit__(self):
        self.c_grafo = new GrafoDisperso()

    def __dealloc__(self):
        del self.c_grafo

    def load_graph(self, filename):
        cdef string c_filename = filename.encode('utf-8')
        self.c_grafo.cargarDatos(c_filename)

    def get_critical_node(self):
        return self.c_grafo.obtenerNodoCritico()

    def run_bfs(self, start_node, depth):
        cdef long long c_start = start_node
        cdef int c_depth = depth
        
        cdef vector[long long] result = self.c_grafo.bfs(c_start, c_depth)
        return result