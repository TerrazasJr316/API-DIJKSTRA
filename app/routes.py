# app/routes.py
from flask import Blueprint, render_template, request
import networkx as nx
import matplotlib.pyplot as plt
import os
from .dijkstra import dijkstra

views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
def index():
    result = None
    path_img = None

    if request.method == "POST":
        data = request.form["data"]
        start = request.form["start"]
        end = request.form["end"]

        graph = {}
        lines = data.strip().split("\n")

        for line in lines:
            src, dest, dist = line.split()
            dist = int(dist)
            graph.setdefault(src, []).append((dest, dist))
            graph.setdefault(dest, []).append((src, dist))  # Grafo no dirigido

        cost, path = dijkstra(graph, start, end)

        if cost == float("inf"):
            result = f"No hay ruta entre {start} y {end}"
        else:
            result = f"Ruta más corta de {start} a {end}: {' -> '.join(path)} (Distancia: {cost})"

        # Visualización del grafo
        G = nx.Graph()
        for src in graph:
            for dest, weight in graph[src]:
                G.add_edge(src, dest, weight=weight)

        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'weight')

        # Dibujar nodos y etiquetas
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=15)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # Resaltar la ruta más corta si existe
        if cost != float("inf"):
            path_edges = list(zip(path, path[1:]))  # Crear pares de nodos en la ruta
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)

        # Guardar la imagen del grafo
        if not os.path.exists("app/static"):
            os.makedirs("app/static")

        path_img = "static/grafo.png"
        plt.savefig("app/" + path_img)
        plt.clf()

    return render_template("index.html", result=result, graph_img=path_img)
