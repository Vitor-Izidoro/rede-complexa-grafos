import pandas as pd
from collections import defaultdict

def carregar_dados_padronizados(caminho_arquivo):
    """
    Carrega e padroniza os dados do CSV, filtrando apenas linhas com 'cast' e 'director' válidos.

    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV.

    Returns:
        tuple: (elencos, diretores), listas de listas com atores e diretores padronizados.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return [], []

    # Filtra linhas com valores não nulos em 'cast' e 'director'
    df = df[df['cast'].notnull() & df['director'].notnull()]

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

        # Padronizar nomes dos diretores,
        
        diretores_padronizados = [d.strip().upper() for d in diretor_raw.split(',') if d.strip()]
        # Não exige mais diretores obrigatórios

        elencos.append(atores)
        diretores.append(diretores_padronizados)
        linhas_processadas += 1

    print(f"\n>>> Linhas processadas: {linhas_processadas} de {total_linhas} válidas.")

    return elencos, diretores


class Grafo:
    """
    Estrutura de Grafo com suporte a grafos direcionados e não direcionados.
    """
    def __init__(self, direcionado=False):
        self.lista_adj = defaultdict(list)  # Lista de adjacência
        self.vertices = set()               # Conjunto de vértices
        self.direcionado = direcionado
        self.num_arestas = 0

    def adicionar_vertice(self, v):
        """Adiciona um vértice ao grafo."""
        self.vertices.add(v)

    def adicionar_aresta(self, u, v, peso=1):
        """
        Adiciona uma aresta entre os vértices u e v.

        Se o grafo for não-direcionado, adiciona a aresta nos dois sentidos.

        Args:
            u (str): Vértice de origem.
            v (str): Vértice de destino.
            peso (int, optional): Peso da aresta. Default é 1.
        """
        self.vertices.update([u, v])

        # Verifica se a aresta já existe para somar peso
        for idx, (viz, peso_atual) in enumerate(self.lista_adj[u]):
            if viz == v:
                self.lista_adj[u][idx] = (viz, peso_atual + peso)
                if not self.direcionado:
                    for jdx, (viz2, peso_atual2) in enumerate(self.lista_adj[v]):
                        if viz2 == u:
                            self.lista_adj[v][jdx] = (viz2, peso_atual2 + peso)
                return

        # Se a aresta ainda não existe, cria
        self.lista_adj[u].append((v, peso))
        self.num_arestas += 1

        if not self.direcionado:
            # Adiciona a aresta inversa se ainda não existir
            if not any(viz == u for viz, _ in self.lista_adj[v]):
                self.lista_adj[v].append((u, peso))

    def obter_info(self):
        """Retorna o número de vértices e de arestas do grafo."""
        num_vertices = len(self.vertices)
        num_arestas = self.num_arestas if self.direcionado else self.num_arestas 
        return num_vertices, num_arestas

    def __str__(self):
        """Gera uma representação textual do grafo."""
        tipo = "direcionado" if self.direcionado else "não direcionado"
        saida = f"Grafo {tipo}\n"
        saida += f"Vértices: {len(self.vertices)}, Arestas: {self.num_arestas if self.direcionado else self.num_arestas }\n"

        for vertice in sorted(self.vertices):
            vizinhos = ", ".join(f"{v}({p})" for v, p in self.lista_adj[vertice])
            saida += f"{vertice}: {vizinhos}\n"

        return saida


def construir_grafo_participantes(elencos, diretores, tipo='atores'):
    """
    Constrói um grafo não direcionado entre atores ou entre diretores.
    - tipo='atores': grafo de atores (vértices = atores, arestas = atuaram juntos)
    - tipo='diretores': grafo de diretores (vértices = diretores, arestas = dirigiram o mesmo ator)
    """
    grafo = Grafo(direcionado=False)
    if tipo == 'atores':
        for elenco in elencos:
            for i in range(len(elenco)):
                for j in range(i + 1, len(elenco)):
                    grafo.adicionar_aresta(elenco[i], elenco[j], 1)
    elif tipo == 'diretores':
        from collections import defaultdict
        ator_para_diretores = defaultdict(set)
        for elenco, diretores_filme in zip(elencos, diretores):
            for ator in elenco:
                for diretor in diretores_filme:
                    ator_para_diretores[ator].add(diretor)
        for diretores_set in ator_para_diretores.values():
            diretores_list = list(diretores_set)
            for i in range(len(diretores_list)):
                for j in range(i + 1, len(diretores_list)):
                    grafo.adicionar_aresta(diretores_list[i], diretores_list[j], 1)
    else:
        raise ValueError("Tipo deve ser 'atores' ou 'diretores'")
    return grafo

def construir_grafo_direcional(elencos, diretores):
    """
    Constrói um grafo direcionado de atores para diretores.
    Vértices: atores e diretores.
    Arestas: de cada ator para cada diretor do mesmo filme.
    """
    grafo = Grafo(direcionado=True)
    for elenco, diretores_filme in zip(elencos, diretores):
        for ator in elenco:
            for diretor in diretores_filme:
                grafo.adicionar_aresta(ator, diretor, 1)
    return grafo

# Exemplo de uso:
# grafo_atores = construir_grafo_participantes(elencos, diretores, tipo='atores')
# grafo_diretores = construir_grafo_participantes(elencos, diretores, tipo='diretores')
# grafo_direcional = construir_grafo_direcional(elencos, diretores)

