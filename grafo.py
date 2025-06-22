import os
import pandas as pd
from collections import defaultdict

# ========== LEITURA E PADRONIZAÇÃO DOS DADOS ==========

def carregar_dados_padronizados(caminho_arquivo):
    """
    Carrega e padroniza os dados do CSV, mantendo apenas linhas com 'cast' e 'director' válidos.

    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV.

    Returns:
        tuple: (elencos, diretores), listas de listas com nomes padronizados em maiúsculo.
    """
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo não encontrado em {caminho_arquivo}")
        return [], []

    try:
        df = pd.read_csv(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return [], []
    
    df = df[df['cast'].notnull() & df['director'].notnull()]

    df.dropna(subset=['cast', 'director'], inplace=True)
    if df.empty:
        print("Nenhum dado válido encontrado após o filtro de nulos.")
        return [], []

    total_linhas = len(df)
    linhas_processadas = 0
    elencos, diretores = [], []

    for _, linha in df.iterrows():
        elenco_raw = linha['cast']
        diretor_raw = linha['director']

        # Padronizar nomes dos atores
        atores = [ator.strip().upper() for ator in elenco_raw.split(',') if ator.strip()]
        if len(atores) == 0:
            continue  # Ignora se não houver nenhum ator

        # Padronizar nomes dos diretores
        diretores_padronizados = [d.strip().upper() for d in diretor_raw.split(',') if d.strip()]
        # Não exige mais diretores obrigatórios

        elencos.append(atores)
        diretores.append(diretores_padronizados)
        linhas_processadas += 1

    print(f"\n>>> Linhas processadas: {linhas_processadas} de {total_linhas} válidas.")

    return elencos, diretores

# ========== CLASSE GRAFO ==========

class Grafo:
    """
    Estrutura de Grafo com suporte a grafos direcionados e não direcionados.
    """
    def __init__(self, direcionado=False):
        self.lista_adj = defaultdict(list)
        self.vertices = set()
        self.direcionado = direcionado
        self.num_arestas = 0

    def adicionar_vertice(self, v):
        """Adiciona um vértice ao grafo."""
        self.vertices.add(v)

    def adicionar_aresta(self, u, v, peso=1):
        """
        Adiciona uma aresta (u, v) ao grafo.

        Para grafos não direcionados, adiciona nos dois sentidos.
        """
        self.vertices.update([u, v])

        # Se a aresta já existe, apenas incrementa o peso
        for idx, (viz, peso_atual) in enumerate(self.lista_adj[u]):
            if viz == v:
                self.lista_adj[u][idx] = (viz, peso_atual + peso)
                if not self.direcionado:
                    for jdx, (viz2, peso_atual2) in enumerate(self.lista_adj[v]):
                        if viz2 == u:
                            self.lista_adj[v][jdx] = (viz2, peso_atual2 + peso)
                return

        # Se a aresta ainda não existe, cria nova
        self.lista_adj[u].append((v, peso))
        self.num_arestas += 1

        if not self.direcionado:
            if not any(viz == u for viz, _ in self.lista_adj[v]):
                self.lista_adj[v].append((u, peso))

    def obter_info(self):
        """Retorna (número de vértices, número de arestas)."""
        num_vertices = len(self.vertices)
        num_arestas = self.num_arestas if self.direcionado else self.num_arestas // 2
        return num_vertices, num_arestas

    def __str__(self):
        """Retorna uma string com a representação do grafo."""
        tipo = "direcionado" if self.direcionado else "não direcionado"
        saida = f"Grafo {tipo}\n"
        saida += f"Vértices: {len(self.vertices)}, Arestas: {self.num_arestas if self.direcionado else self.num_arestas // 2}\n"

        for vertice in sorted(self.vertices):
            vizinhos = ", ".join(f"{v}({p})" for v, p in self.lista_adj[vertice])
            saida += f"{vertice}: {vizinhos}\n"

        return saida

# ========== CONSTRUÇÃO DOS GRAFOS ==========

def construir_grafo_atores(elencos):
    """
    Constrói o grafo de co-atores (não direcionado).
    Cada aresta indica que os dois atores trabalharam juntos.

    Args:
        elencos (list): Lista de listas de atores.

    Returns:
        Grafo: Grafo não direcionado.
    """
    grafo = Grafo(direcionado=False)

    for elenco in elencos:
        for i in range(len(elenco)):
            for j in range(i + 1, len(elenco)):
                grafo.adicionar_aresta(elenco[i], elenco[j], 1)

    return grafo

def construir_grafo_direcional(elencos, diretores):
    """
    Constrói o grafo bipartido direcionado de atores → diretores.

    Cada aresta indica que o ator trabalhou com o diretor.

    Args:
        elencos (list): Lista de listas de atores.
        diretores (list): Lista de listas de diretores.

    Returns:
        Grafo: Grafo direcionado.
    """
    grafo = Grafo(direcionado=True)

    for elenco, diretores_filme in zip(elencos, diretores):
        for ator in elenco:
            for diretor in diretores_filme:
                grafo.adicionar_aresta(ator, diretor, 1)

    return grafo
