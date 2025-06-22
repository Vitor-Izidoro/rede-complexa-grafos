import os
import platform
from collections import defaultdict
from grafo import carregar_dados_padronizados, construir_grafo_atores, construir_grafo_direcional
from algoritmos import (
    componentes_conexas,
    componentes_fortemente_conexas,
    agm_prim,
    degree_centrality,
    betweenness_centrality,
    closeness_centrality
)

# ========== UTILITÁRIOS ==========

def limpar_terminal():
    os.system("cls" if platform.system() == "Windows" else "clear")

def salvar_em_txt(nome_arquivo, conteudo):
    os.makedirs("resultados", exist_ok=True)
    caminho = os.path.join("resultados", nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

def imprimir_agm_completa(agm, raiz):
    adj = defaultdict(list)
    for u, v, p in agm:
        adj[u].append((v, p))
        adj[v].append((u, p))

    linhas = []
    visitado = set()

    def dfs(no, prefix=""):
        visitado.add(no)
        linhas.append(prefix + no)
        filhos = [(v, p) for v, p in sorted(adj[no], key=lambda x: x[0]) if v not in visitado]
        for i, (filho, peso) in enumerate(filhos):
            marcador = "└── " if i == len(filhos) - 1 else "├── "
            linhas.append(f"{prefix}{marcador}{filho} ({peso})")
            dfs(filho, prefix + ("    " if i == len(filhos) - 1 else "│   "))

    dfs(raiz)
    return "\n".join(linhas)

def salvar_agm_completa_em_txt(agm, raiz):
    conteudo = imprimir_agm_completa(agm, raiz)
    salvar_em_txt("agm_completa.txt", conteudo)
    print(f"\nÁrvore Geradora Mínima COMPLETA salva em 'resultados/agm_completa.txt'\n")

# ========== MENU E EXECUÇÃO DE OPÇÕES ==========

def mostrar_menu():
    print("""
===== ANÁLISE DE REDES COMPLEXAS =====
1. Informações básicas dos grafos
2. Componentes conexas
3. Árvore Geradora Mínima (grafo atores)
4. Centralidade de Grau - Atores (não direcionado)
5. Centralidade de Intermediação - Atores (não direcionado)
6. Centralidade de Proximidade - Atores (não direcionado)
7. Centralidade de Grau - Diretores (grafo direcionado)
8. Centralidade de Intermediação - Diretores (grafo direcionado)
9. Centralidade de Proximidade - Diretores (grafo direcionado)
0. Sair
======================================
""")
    return input("Escolha uma opção: ").strip()

def executar_opcao(opcao, grafo_atores, grafo_direcional):
    conteudo = ""

    if opcao == "1":
        v1, a1 = grafo_atores.obter_info()
        v2, a2 = grafo_direcional.obter_info()
        conteudo += f"\n--- INFORMAÇÕES BÁSICAS DOS GRAFOS ---\n"
        conteudo += f"Grafo de Atores: {v1} vértices, {a1} arestas\n"
        conteudo += f"Grafo Direcional: {v2} vértices, {a2} arestas\n"

    elif opcao == "2":
        comp_nao_dir = componentes_conexas(grafo_atores)
        comp_dir = componentes_fortemente_conexas(grafo_direcional)
        conteudo += f"\n--- COMPONENTES CONEXAS ---\n"
        conteudo += f"Grafo de Atores: {len(comp_nao_dir)} componentes conexas\n"
        conteudo += f"Grafo Direcional: {len(comp_dir)} componentes fortemente conexas\n"

    elif opcao == "3":
        conteudo += "\n--- ÁRVORE GERADORA MÍNIMA (PRIM) ---\n"
        print("1 - Informar vértice manualmente")
        print("2 - Escolher automaticamente o primeiro vértice disponível")
        escolha = input("Opção (1 ou 2): ").strip()

        if escolha == "1":
            raiz = input("Informe o nome do vértice inicial: ").strip()
            if raiz not in grafo_atores.vertices:
                conteudo += f"Vértice '{raiz}' não encontrado.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                return
        elif escolha == "2":
            if not grafo_atores.vertices:
                conteudo += "O grafo de atores está vazio.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                return
            raiz = next(iter(grafo_atores.vertices))
            conteudo += f"Raiz escolhida automaticamente: {raiz}\n"
        else:
            conteudo += "Opção inválida.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_3.txt", conteudo)
            return

        agm, custo = agm_prim(grafo_atores, raiz)
        if not agm:
            conteudo += "Não foi possível gerar a AGM. Verifique se o grafo é conexo.\n"
        else:
            conteudo += f"\nCusto total da AGM: {custo}\n"
            salvar_agm_completa_em_txt(agm, raiz)

    elif opcao == "4":
        conteudo += "\n--- CENTRALIDADE DE GRAU - ATORES ---\n"
        graus = degree_centrality(grafo_atores, normalizar=True)
        for v, (g, norm) in sorted(graus.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"

    elif opcao == "5":
        conteudo += "\n--- CENTRALIDADE DE INTERMEDIAÇÃO - ATORES ---\n"
        centralidade = betweenness_centrality(grafo_atores, normalizar=True)
        for v, (c, norm) in sorted(centralidade.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"

    elif opcao == "6":
        print("\n--- CENTRALIDADE DE PROXIMIDADE (CLOSENESS) ---")
        componentes = componentes_conexas(grafo_atores)
        maior_componente = max(componentes, key=len)
        centralidade = closeness_centrality(grafo_atores, vertices=maior_componente)
        print("Top 10 vértices por proximidade:")
        def get_val(x):
            if isinstance(x, tuple):
                return x[0]
            return x
        top10 = sorted(centralidade.items(), key=lambda x: -get_val(x[1]))[:10]
        for v, c in top10:
            if isinstance(c, tuple):
                if len(c) > 1:
                    print(f"{v}: {c[0]:.4f} (normalizado: {c[1]:.4f})")
                else:
                    print(f"{v}: {c[0]:.4f}")
            else:
                print(f"{v}: {c:.4f}")

    elif opcao == "7":
        conteudo += "\n--- CENTRALIDADE DE GRAU - DIRETORES ---\n"
        graus = degree_centrality(grafo_direcional, mode="in", normalizar=True)
        for v, (g, norm) in sorted(graus.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"

    elif opcao == "8":
        conteudo += "\n--- CENTRALIDADE DE INTERMEDIAÇÃO - DIRETORES ---\n"
        centralidade = betweenness_centrality(grafo_direcional, normalizar=True)
        for v, (c, norm) in sorted(centralidade.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"

    elif opcao == "9":
        conteudo += "\n--- CENTRALIDADE DE PROXIMIDADE - DIRETORES ---\n"
        centralidade = closeness_centrality(grafo_direcional, normalizar=True)
        for v, (c, norm) in sorted(centralidade.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"


    elif opcao == "0":
        print("Saindo do programa... Até mais!")
        exit()

    else:
        print("Opção inválida.\n")
        return

    # Exibir no terminal e salvar em txt
    print(conteudo)
    salvar_em_txt(f"saida_opcao_{opcao}.txt", conteudo)

# ========== MAIN ==========

def main():
    arquivo_csv = 'netflix_amazon_disney_titles.csv'

    if not os.path.exists(arquivo_csv):
        print(f"ERRO: O arquivo '{arquivo_csv}' não foi encontrado na pasta atual.")
        return

    print("Carregando dados do arquivo...")
    elencos, diretores = carregar_dados_padronizados(arquivo_csv)

    print("Construindo grafos...")
    grafo_atores = construir_grafo_atores(elencos)
    grafo_direcional = construir_grafo_direcional(elencos, diretores)
    print("Grafos criados com sucesso!")

    while True:
        opcao = mostrar_menu()
        executar_opcao(opcao, grafo_atores, grafo_direcional)
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
