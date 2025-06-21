from collections import deque, defaultdict
import heapq

# ========== COMPONENTES CONEXAS ==========

def componentes_conexas(grafo):
    print("Calculando componentes conexas...")
    visitado = set()
    componentes = []
    total, cont = len(grafo.vertices), 0

    for v in grafo.vertices:
        cont += 1
        print(f"Componentes conexas: {cont}/{total} vértices processados...", end='\r', flush=True)
        if v not in visitado:
            componente = []
            pilha = [v]
            while pilha:
                atual = pilha.pop()
                if atual not in visitado:
                    visitado.add(atual)
                    componente.append(atual)
                    for vizinho, _ in grafo.lista_adj.get(atual, []):
                        if vizinho not in visitado:
                            pilha.append(vizinho)
            componentes.append(componente)

    print(" " * 50, end='\r')
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

    visitado, pilha = set(), []
    total, cont = len(grafo.vertices), 0

    for v in grafo.vertices:
        cont += 1
        print(f"Passo 1 - DFS direto: {cont}/{total} vértices processados...", end='\r', flush=True)
        if v not in visitado:
            dfs(v, visitado, pilha)

    print(" " * 50, end='\r')

    transposto = defaultdict(list)
    for u in grafo.lista_adj:
        for v, peso in grafo.lista_adj[u]:
            transposto[v].append((u, peso))

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

# ========== ÁRVORE GERADORA MÍNIMA ==========

def agm_prim(grafo, inicio):
    print(f"Calculando Árvore Geradora Mínima a partir do vértice '{inicio}'...")
    visitado, agm, custo_total = set(), [], 0
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

# ========== CENTRALIDADE DE GRAU ==========
def degree_centrality(grafo, mode="total", normalizar=False):
    centralidade = {}
    total, cont = len(grafo.vertices), 0
    n = len(grafo.vertices)

    for v in grafo.vertices:
        cont += 1
        print(f"Centralidade de grau: {cont}/{total} vértices processados...", end='\r', flush=True)

        if grafo.direcionado:
            if mode == "in":
                grau = sum(1 for u in grafo.vertices for w, _ in grafo.lista_adj.get(u, []) if w == v)
            elif mode == "out":
                grau = len(grafo.lista_adj.get(v, []))
            else:
                in_degree = sum(1 for u in grafo.vertices for w, _ in grafo.lista_adj.get(u, []) if w == v)
                out_degree = len(grafo.lista_adj.get(v, []))
                grau = in_degree + out_degree
        else:
            grau = len(grafo.lista_adj.get(v, []))

        norm = grau / (n - 1) if normalizar and n > 1 else grau
        centralidade[v] = (grau, norm)

    print(" " * 50, end='\r')
    return centralidade


def betweenness_centrality(grafo, normalizar=False):
    centralidade = defaultdict(float)
    total, cont = len(grafo.vertices), 0
    n = len(grafo.vertices)

    for s in grafo.vertices:
        cont += 1
        print(f"Betweenness: {cont}/{total} vértices processados...", end='\r', flush=True)

        S, P = [], defaultdict(list)
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
                if sigma[w] != 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                centralidade[w] += delta[w]

    print(" " * 50, end='\r')

    for v in centralidade:
        centralidade[v] /= 2

    resultado = {}
    for v, valor in centralidade.items():
        if normalizar and n > 2:
            norm = (1 / ((n - 1) * (n - 2))) if grafo.direcionado else (2 / ((n - 1) * (n - 2)))
            resultado[v] = (valor, valor * norm)
        else:
            resultado[v] = (valor, valor)

    return resultado


def closeness_centrality(grafo, normalizar=False):
    centralidade = {}
    total, cont = len(grafo.vertices), 0
    n = len(grafo.vertices)

    for v in grafo.vertices:
        cont += 1
        print(f"Centralidade de proximidade: {cont}/{total} vértices processados...", end='\r', flush=True)

        dist = {v: 0}
        fila = deque([v])

        while fila:
            u = fila.popleft()
            for w, _ in grafo.lista_adj.get(u, []):
                if w not in dist:
                    dist[w] = dist[u] + 1
                    fila.append(w)

        reachable = len(dist) - 1
        total_dist = sum(dist.values())

        if reachable > 0 and total_dist > 0:
            valor = reachable / total_dist
            if normalizar and n > 1:
                norm = valor * (n - 1)
            else:
                norm = valor
        else:
            valor = 0.0
            norm = 0.0

        centralidade[v] = (valor, norm)

    print(" " * 50, end='\r')
    return centralidade
