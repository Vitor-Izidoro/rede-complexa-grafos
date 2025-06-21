import platform
import os
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

def limpar_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def mostrar_menu():
    print("\n===== ANÁLISE DE REDES COMPLEXAS =====")
    print("1. Informações básicas dos grafos")
    print("2. Componentes conexas")
    print("3. Árvore Geradora Mínima (grafo atores)")
    print("4. Centralidade de Grau - Atores (não direcionado)")
    print("5. Centralidade de Intermediação - Atores (não direcionado)")
    print("6. Centralidade de Proximidade - Atores (não direcionado)")
    print("7. Centralidade de Grau - Diretores (grafo direcionado)")
    print("8. Centralidade de Intermediação - Diretores (grafo direcionado)")
    print("9. Centralidade de Proximidade - Diretores (grafo direcionado)")
    print("0. Sair")
    print("======================================")
    return input("Escolha uma opção: ").strip()

def imprimir_agm_completa(agm, raiz):
    adj = defaultdict(list)
    for u, v, p in agm:
        adj[u].append((v, p))
        adj[v].append((u, p))

    visitado = set()
    linhas = []

    def dfs(no, prefix=""):
        visitado.add(no)
        linhas.append(prefix + no)
        filhos = [(v, p) for v, p in sorted(adj[no], key=lambda x: x[0]) if v not in visitado]
        for i, (filho, peso) in enumerate(filhos):
            marcador = "└── " if i == len(filhos) - 1 else "├── "
            linhas.append(f"{prefix}{marcador}{filho} ({peso})")
            dfs(filho, prefix + ("    " if i == len(filhos) - 1 else "│   "))

    dfs(raiz)
    return linhas

def salvar_agm_completa_em_txt(agm, raiz, nome_arquivo="agm_completa.txt"):
    linhas = imprimir_agm_completa(agm, raiz)
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"\nÁrvore Geradora Mínima COMPLETA salva em '{nome_arquivo}'.\n")

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

        if opcao == "1":
            print("\n--- INFORMAÇÕES BÁSICAS DOS GRAFOS ---")
            v1, a1 = grafo_atores.obter_info()
            print(f"Grafo de Atores (não direcionado): {v1} vértices, {a1} arestas")
            v2, a2 = grafo_direcional.obter_info()
            print(f"Grafo Direcional (atores → diretores): {v2} vértices, {a2} arestas")

        elif opcao == "2":
            print("\n--- COMPONENTES CONEXAS ---")
            comp_nao_dir = componentes_conexas(grafo_atores)
            print(f"Grafo de Atores: {len(comp_nao_dir)} componentes conexas")
            comp_dir = componentes_fortemente_conexas(grafo_direcional)
            print(f"Grafo Direcional: {len(comp_dir)} componentes fortemente conexas")

        elif opcao == "3":
            print("\n--- ÁRVORE GERADORA MÍNIMA (PRIM) ---")
            print("1 - Informar vértice manualmente")
            print("2 - Escolher automaticamente o primeiro vértice disponível")
            escolha = input("Opção (1 ou 2): ").strip()

            if escolha == "1":
                raiz = input("Informe o nome do vértice inicial: ").strip()
                if raiz not in grafo_atores.vertices:
                    print(f"Vértice '{raiz}' não encontrado.")
                    input("\nPressione Enter para continuar...")
                    continue
            elif escolha == "2":
                if not grafo_atores.vertices:
                    print("O grafo de atores está vazio.")
                    input("\nPressione Enter para continuar...")
                    continue
                raiz = next(iter(grafo_atores.vertices))
                print(f"Raiz escolhida automaticamente: {raiz}")
            else:
                print("Opção inválida.")
                input("\nPressione Enter para continuar...")
                continue

            agm, custo = agm_prim(grafo_atores, raiz)
            if not agm:
                print("Não foi possível gerar a AGM. Verifique se o grafo é conexo.")
                input("\nPressione Enter para continuar...")
                continue

            print(f"\nAGM iniciando em '{raiz}':")
            
            print(f"\nCusto total da AGM: {custo}")
            salvar_agm_completa_em_txt(agm, raiz)

        elif opcao == "4":
            print("\n--- CENTRALIDADE DE GRAU - ATORES (GRAFO NÃO DIRECIONADO) ---")
            graus = degree_centrality(grafo_atores)
            print("Top 10 atores/atrizes com maior grau (número de colaborações com outros atores):")
            for v, g in sorted(graus.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {g}")
            print("\n👉 A centralidade de grau indica com quantos outros atores/atrizes cada ator/atriz trabalhou diretamente.")

        elif opcao == "5":
            print("\n--- CENTRALIDADE DE INTERMEDIAÇÃO - ATORES (GRAFO NÃO DIRECIONADO) ---")
            centralidade = betweenness_centrality(grafo_atores)
            print("Top 10 atores/atrizes com maior intermediação (quantas vezes um ator está no caminho mais curto entre outros atores):")
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {c:.4f}")
            print("\n👉 A centralidade de intermediação mostra quais atores/atrizes são mais importantes como pontes entre outros pares da rede.")

        elif opcao == "6":
            print("\n--- CENTRALIDADE DE PROXIMIDADE - ATORES (GRAFO NÃO DIRECIONADO) ---")
            centralidade = closeness_centrality(grafo_atores)
            print("Top 10 atores/atrizes com maior proximidade (mais próximos dos demais em média):")
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {c:.4f}")
            print("\n👉 A centralidade de proximidade indica quais atores têm menor distância média até todos os outros, sendo os mais acessíveis na rede.")

        elif opcao == "7":
            print("\n--- CENTRALIDADE DE GRAU - DIRETORES (GRAFO DIRECIONADO) ---")
            graus = degree_centrality(grafo_direcional, mode="in")
            print("Top 10 diretores com maior grau de entrada (número de atores que trabalharam com eles):")
            for v, g in sorted(graus.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {g}")
            print("\n👉 A centralidade de grau (entrada) indica quantos atores diferentes trabalharam com cada diretor, ou seja, a quantidade de conexões recebidas pelo diretor.")

        elif opcao == "8":
            print("\n--- CENTRALIDADE DE INTERMEDIAÇÃO - DIRETORES (GRAFO DIRECIONADO) ---")
            centralidade = betweenness_centrality(grafo_direcional)
            print("Top 10 diretores com maior intermediação (pontes entre atores e outros diretores):")
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {c:.4f}")
            print("\n👉 A centralidade de intermediação no grafo direcionado indica quais diretores são mais relevantes como intermediários nos caminhos mais curtos da rede de atores para diretores.")

        elif opcao == "9":
            print("\n--- CENTRALIDADE DE PROXIMIDADE - DIRETORES (GRAFO DIRECIONADO) ---")
            centralidade = closeness_centrality(grafo_direcional)
            print("Top 10 diretores com maior proximidade (menor distância média até os outros vértices):")
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {c:.4f}")
            print("\n👉 A centralidade de proximidade indica quais diretores estão mais próximos dos outros na rede, ou seja, têm menor distância média até os atores e demais diretores.")

        elif opcao == "0":
            confirm = input("Tem certeza que deseja sair? (s/n): ").strip().lower()
            if confirm == "s":
                print("Saindo do programa... Até mais!")
                break

        else:
            print("Opção inválida.")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
