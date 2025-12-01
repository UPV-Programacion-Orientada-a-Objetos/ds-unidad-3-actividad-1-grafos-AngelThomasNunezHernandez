import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

try:
    import neuronet
except ImportError:
    print("Error: No se encontró el módulo 'neuronet'. Ejecuta 'python setup.py build_ext --inplace' primero.")
    exit()

class NeuroNetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroNet: Análisis de Redes Masivas (C++ Kernel)")
        self.root.geometry("900x700")

        self.engine = neuronet.NeuroNetEngine()
        self.graph_loaded = False

        self._init_ui()

    def _init_ui(self):
        control_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="1. Cargar Dataset (SNAP)", command=self.load_data, bg="#4a7abc", fg="white")
        btn_load.pack(side=tk.LEFT, padx=5)

        btn_crit = tk.Button(control_frame, text="2. Analizar Nodo Crítico", command=self.find_critical, state=tk.DISABLED)
        self.btn_crit = btn_crit
        btn_crit.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Nodo Inicio:").pack(side=tk.LEFT, padx=5)
        self.entry_start = tk.Entry(control_frame, width=10)
        self.entry_start.pack(side=tk.LEFT)
        
        tk.Label(control_frame, text="Profundidad:").pack(side=tk.LEFT, padx=5)
        self.entry_depth = tk.Entry(control_frame, width=5)
        self.entry_depth.insert(0, "2")
        self.entry_depth.pack(side=tk.LEFT)

        btn_bfs = tk.Button(control_frame, text="3. Visualizar Propagación (BFS)", command=self.run_visualization, state=tk.DISABLED)
        self.btn_bfs = btn_bfs
        btn_bfs.pack(side=tk.LEFT, padx=5)

        self.log_label = tk.Label(self.root, text="Sistema listo.", anchor="w", bg="black", fg="#00ff00", font=("Consolas", 10))
        self.log_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_label.config(text=f"> {msg}")
        self.root.update()

    def load_data(self):
        file_path = filedialog.askopenfilename(title="Seleccionar Dataset SNAP", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.log("Cargando grafo en motor C++ (CSR)... Espere...")
            start_time = time.time()
            
            try:
                self.engine.load_graph(file_path)
                elapsed = time.time() - start_time
                self.log(f"Grafo cargado exitosamente en {elapsed:.4f} seg. Memoria optimizada.")
                self.graph_loaded = True
                self.btn_crit.config(state=tk.NORMAL)
                self.btn_bfs.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def find_critical(self):
        if not self.graph_loaded: return
        node_id = self.engine.get_critical_node()
        messagebox.showinfo("Análisis Topológico", f"El nodo más crítico (mayor grado) es el ID: {node_id}")
        self.entry_start.delete(0, tk.END)
        self.entry_start.insert(0, str(node_id))

    def run_visualization(self):
        try:
            start_node = int(self.entry_start.get())
            depth = int(self.entry_depth.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
            return

        self.log(f"Ejecutando BFS Nativo desde nodo {start_node}...")
        
        raw_edges = self.engine.run_bfs(start_node, depth)
        
        if not raw_edges:
            self.log("No se encontraron conexiones o nodo inválido.")
            return

        self.log(f"Renderizando subgrafo con {len(raw_edges)//2} aristas...")
        
        self.ax.clear()
        G_viz = nx.Graph()
        
        for i in range(0, len(raw_edges), 2):
            u, v = raw_edges[i], raw_edges[i+1]
            G_viz.add_edge(u, v)

        pos = nx.spring_layout(G_viz, seed=42)
        
        node_colors = ['red' if node == start_node else 'skyblue' for node in G_viz.nodes()]
        
        nx.draw(G_viz, pos, ax=self.ax, with_labels=True, node_size=300, 
                node_color=node_colors, font_size=8, edge_color="gray")
        
        self.canvas.draw()
        self.log("Visualización completada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroNetApp(root)
    root.mainloop()