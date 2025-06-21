from grafo import carregar_dados_padronizados, construir_grafo_atores, construir_grafo_direcional
from algoritmos import (
    componentes_conexas,
    componentes_fortemente_conexas,
    agm_prim,
    degree_centrality,
    betweenness_centrality,
    closeness_centrality
)
import os
import random

def mostrar_menu():
    print("\n===== ANÁLISE DE REDES COMPLEXAS =====")
    print("1. Informações básicas dos grafos")
    print("2. Componentes conexas")
    print("3. Árvore Geradora Mínima (grafo atores)")
    print("4. Centralidade de Grau")
    print("5. Centralidade de Intermediação")
    print("6. Centralidade de Proximidade")
    print("0. Sair")
    print("======================================")
    return input("Escolha uma opção: ").strip()

def main():
    """
    Programa principal para análise de redes complexas a partir de dados de filmes/series.
    """
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
            print("Deseja escolher um vértice inicial ou deixar o programa escolher automaticamente?")
            print("1 - Informar vértice manualmente")
            print("2 - Escolher automaticamente o primeiro vértice disponível")
            escolha = input("Opção (1 ou 2): ").strip()

            if escolha == "1":
                raiz = input("Informe o nome do vértice inicial: ").strip().upper()
                if raiz not in grafo_atores.vertices:
                    print(f"Vértice '{raiz}' não encontrado no grafo de atores.")
                else:
                    agm, custo = agm_prim(grafo_atores, raiz)
                    print(f"\nÁrvore Geradora Mínima iniciando em '{raiz}':")
                    for u, v, peso in agm:
                        print(f"{u} --({peso})-- {v}")
                    print(f"Custo total da AGM: {custo}")

            elif escolha == "2":
                if not grafo_atores.vertices:
                    print("O grafo de atores está vazio. Não é possível calcular a AGM.")
                else:
                    raiz = next(iter(grafo_atores.vertices))
                    print(f"Vértice '{raiz}' escolhido automaticamente como raiz.\n")
                    agm, custo = agm_prim(grafo_atores, raiz)
                    print(f"\nÁrvore Geradora Mínima iniciando em '{raiz}':")
                    for u, v, peso in agm:
                        print(f"{u} --({peso})-- {v}")
                    print(f"Custo total da AGM: {custo}")
            else:
                print("Opção inválida. Voltando ao menu principal.")

        elif opcao == "4":
            print("\n--- CENTRALIDADE DE GRAU ---")
            graus_atores = degree_centrality(grafo_atores)
            graus_direcional = degree_centrality(grafo_direcional)

            print("\nTop 10 vértices com maior grau (Grafo de Atores):")
            for v, g in sorted(graus_atores.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {g}")

            print("\nTop 10 vértices com maior grau (Grafo Direcional):")
            for v, g in sorted(graus_direcional.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {g}")

        elif opcao == "5":
            print("\n--- CENTRALIDADE DE INTERMEDIAÇÃO (BETWEENNESS) ---")
            centralidade = betweenness_centrality(grafo_atores)
            print("Top 10 vértices por intermediação:")
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                print(f"{v}: {c:.4f}")

        elif opcao == "6":
            print("\n--- CENTRALIDADE DE PROXIMIDADE (CLOSENESS) ---")
            
            componentes = componentes_conexas(grafo_atores)
            maior_componente = max(componentes, key=len)
            amostra = random.sample(list(maior_componente), 100)


            centralidade = closeness_centrality(grafo_atores, vertices=maior_componente)

            print("Top 10 vértices por proximidade (entre 100 amostrados):")
            top10 = sorted(centralidade.items(), key=lambda x: -x[1])[:10]
            for v, c in top10:
                print(f"{v}: {c:.4f}")

        elif opcao == "0":
            confirm = input("Tem certeza que deseja sair? (s/n): ").strip().lower()
            if confirm == "s":
                print("Saindo do programa... Até mais!")
                break
            else:
                print("Cancelado. Voltando ao menu principal.")

        else:
            print("Opção inválida. Por favor, selecione uma opção válida do menu.")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()