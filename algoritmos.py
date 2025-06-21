from collections import deque, defaultdict
import heapq

def componentes_conexas(grafo):
    print("Calculando componentes conexas...")
    visitado = set()
    componentes = []

    total = len(grafo.vertices)
    cont = 0

    for v in grafo.vertices:
        cont += 1
        print(f"Componentes conexas: {cont}/{total} vértices processados...", end='\r', flush=True)

        if v not in visitado:
            pilha = [v]
            componente = []

            while pilha:
                atual = pilha.pop()
                if atual not in visitado:
                    visitado.add(atual)
                    componente.append(atual)
                    for vizinho, _ in grafo.lista_adj.get(atual, []):
                        if vizinho not in visitado:
                            pilha.append(vizinho)

            componentes.append(componente)

    print(" " * 50, end='\r')  # limpa a linha
    print(f"Componentes conexas calculadas: {len(componentes)} componentes encontradas.")
    return componentes


def componentes_fortemente_conexas(grafo):
    print("Calculando componentes fortemente conexas...")
    def dfs(v, visitado, pilha):
        visitado.add(v)
        for viz, _ in grafo.lista_adj.get(v, []):
            if viz not in visitado:
                dfs(viz, visitado, pilha)
        pilha.append(v)

    def dfs_transposto(v, visitado, componente, transposto):
        visitado.add(v)
        componente.append(v)
        for viz, _ in transposto.get(v, []):
            if viz not in visitado:
                dfs_transposto(viz, visitado, componente, transposto)

    visitado = set()
    pilha = []
    total = len(grafo.vertices)
    cont = 0
    for v in grafo.vertices:
        cont += 1
        print(f"Componentes fortemente conexas (passagem 1): {cont}/{total} vértices processados...", end='\r', flush=True)
        if v not in visitado:
            dfs(v, visitado, pilha)

    print(" " * 50, end='\r')  # limpa a linha

    transposto = {}
    for u in grafo.lista_adj:
        for v, peso in grafo.lista_adj[u]:
            transposto.setdefault(v, []).append((u, peso))

    visitado.clear()
    componentes = []
    while pilha:
        v = pilha.pop()
        if v not in visitado:
            componente = []
            dfs_transposto(v, visitado, componente, transposto)
            componentes.append(componente)

    print(f"Componentes fortemente conexas calculadas: {len(componentes)} componentes encontradas.")
    return componentes


def agm_prim(grafo, inicio):
    print(f"Calculando Árvore Geradora Mínima a partir do vértice '{inicio}'...")
    visitado = set()
    agm = []
    custo_total = 0
    fila = []

    visitado.add(inicio)
    for viz, peso in grafo.lista_adj.get(inicio, []):
        heapq.heappush(fila, (peso, inicio, viz))

    while fila:
        peso, u, v = heapq.heappop(fila)
        if v not in visitado:
            visitado.add(v)
            agm.append((u, v, peso))
            custo_total += peso
            for viz, p in grafo.lista_adj.get(v, []):
                if viz not in visitado:
                    heapq.heappush(fila, (p, v, viz))

    print(f"AGM calculada com custo total: {custo_total}")
    return agm, custo_total


def degree_centrality(grafo):
    print("Calculando centralidade de grau...")
    centralidade = {}
    total = len(grafo.vertices)
    cont = 0
    for v in grafo.vertices:
        cont += 1
        print(f"Centralidade de grau: {cont}/{total} vértices processados...", end='\r', flush=True)
        centralidade[v] = len(grafo.lista_adj.get(v, []))
    print(" " * 50, end='\r')  # limpa a linha
    print("Centralidade de grau calculada.")
    return centralidade


def betweenness_centrality(grafo):
    print("Calculando centralidade de intermediação (betweenness)...")
    centralidade = defaultdict(float)
    total = len(grafo.vertices)
    cont = 0

    for s in grafo.vertices:
        cont += 1
        print(f"Betweenness: {cont}/{total} vértices processados...", end='\r', flush=True)

        S = []
        P = defaultdict(list)
        sigma = dict.fromkeys(grafo.vertices, 0)
        d = dict.fromkeys(grafo.vertices, -1)
        sigma[s], d[s] = 1, 0
        Q = deque([s])

        while Q:
            v = Q.popleft()
            S.append(v)
            for w, _ in grafo.lista_adj.get(v, []):
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)

        delta = dict.fromkeys(grafo.vertices, 0)
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]) if sigma[w] != 0 else 0
            if w != s:
                centralidade[w] += delta[w]

    print(" " * 50, end='\r')  # limpa a linha
    for v in centralidade:
        centralidade[v] /= 2
    print("Centralidade de intermediação calculada.")
    return dict(centralidade)
def closeness_centrality(grafo, vertices=None):
    from collections import deque

    print("Calculando centralidade de proximidade...")
    centralidade = {}
    vertices = vertices or grafo.vertices  # permite calcular para subconjuntos, como a maior componente
    total = len(vertices)

    for idx, v in enumerate(vertices):
        print(f"Centralidade de proximidade: {idx+1}/{total} vértices processados...", end='\r', flush=True)

        dist = {v: 0}
        fila = deque([v])
        while fila:
            u = fila.popleft()
            for w, _ in grafo.lista_adj.get(u, []):
                if w not in dist:
                    dist[w] = dist[u] + 1
                    fila.append(w)

        alcançados = len(dist) - 1
        if alcançados > 0:
            soma = sum(dist.values())
            centralidade[v] = alcançados / soma
        else:
            centralidade[v] = 0

    print(" " * 50, end='\r')
    print("Centralidade de proximidade calculada.")
    return centralidade