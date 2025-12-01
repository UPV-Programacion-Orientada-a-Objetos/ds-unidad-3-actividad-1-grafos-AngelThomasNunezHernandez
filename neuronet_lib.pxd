from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "GraphCore.h":
    cdef cppclass GrafoBase:
        pass

    cdef cppclass GrafoDisperso(GrafoBase):
        GrafoDisperso() except +
        void cargarDatos(string filename)
        vector[long long] bfs(long long startNodeID, int maxDepth) 
        long long obtenerNodoCritico()