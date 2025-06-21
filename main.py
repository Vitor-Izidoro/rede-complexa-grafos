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
    closeness_centrality,
    grau_normalizado,
    betweenness_normalizado,
    closeness_normalizado
)

def limpar_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def mostrar_menu():
    print("""
        \n===== ANÁLISE DE REDES COMPLEXAS =====
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

os.makedirs("resultados", exist_ok=True)

def salvar_em_txt(nome_arquivo, conteudo):
    caminho = os.path.join("resultados", nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

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
            conteudo = "\n--- INFORMAÇÕES BÁSICAS DOS GRAFOS ---\n"
            v1, a1 = grafo_atores.obter_info()
            conteudo += f"Grafo de Atores (não direcionado): {v1} vértices, {a1} arestas\n"
            v2, a2 = grafo_direcional.obter_info()
            conteudo += f"Grafo Direcional (atores → diretores): {v2} vértices, {a2} arestas\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_1.txt", conteudo)

        elif opcao == "2":
            conteudo = "\n--- COMPONENTES CONEXAS ---\n"
            comp_nao_dir = componentes_conexas(grafo_atores)
            conteudo += f"Grafo de Atores: {len(comp_nao_dir)} componentes conexas\n"
            comp_dir = componentes_fortemente_conexas(grafo_direcional)
            conteudo += f"Grafo Direcional: {len(comp_dir)} componentes fortemente conexas\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_2.txt", conteudo)

        elif opcao == "3":
            conteudo = "\n--- ÁRVORE GERADORA MÍNIMA (PRIM) ---\n"
            print("1 - Informar vértice manualmente")
            print("2 - Escolher automaticamente o primeiro vértice disponível")
            escolha = input("Opção (1 ou 2): ").strip()

            if escolha == "1":
                raiz = input("Informe o nome do vértice inicial: ").strip()
                if raiz not in grafo_atores.vertices:
                    conteudo += f"Vértice '{raiz}' não encontrado.\n"
                    print(conteudo)
                    salvar_em_txt("saida_opcao_3.txt", conteudo)
                    input("\nPressione Enter para continuar...")
                    continue
            elif escolha == "2":
                if not grafo_atores.vertices:
                    conteudo += "O grafo de atores está vazio.\n"
                    print(conteudo)
                    salvar_em_txt("saida_opcao_3.txt", conteudo)
                    input("\nPressione Enter para continuar...")
                    continue
                raiz = next(iter(grafo_atores.vertices))
                conteudo += f"Raiz escolhida automaticamente: {raiz}\n"
            else:
                conteudo += "Opção inválida.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                input("\nPressione Enter para continuar...")
                continue

            agm, custo = agm_prim(grafo_atores, raiz)
            if not agm:
                conteudo += "Não foi possível gerar a AGM. Verifique se o grafo é conexo.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                input("\nPressione Enter para continuar...")
                continue

            conteudo += f"\nCusto total da AGM: {custo}\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_3.txt", conteudo)
            salvar_agm_completa_em_txt(agm, raiz)  # Isso já deve salvar a AGM em outro txt próprio.

        elif opcao == "4":
            conteudo = "\n--- CENTRALIDADE DE GRAU - ATORES (GRAFO NÃO DIRECIONADO) ---\n"
            graus = degree_centrality(grafo_atores)
            conteudo += "Top 10 atores/atrizes com maior grau:\n"
            for v, g in sorted(graus.items(), key=lambda x: -x[1])[:10]:
                norm = grau_normalizado(grafo_atores, v)
                conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de grau indica com quantos outros atores/atrizes cada ator/atriz trabalhou diretamente.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_4.txt", conteudo)

        elif opcao == "5":
            conteudo = "\n--- CENTRALIDADE DE INTERMEDIAÇÃO - ATORES ---\n"
            centralidade = betweenness_centrality(grafo_atores)
            conteudo += "Top 10 atores/atrizes com maior intermediação:\n"
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                norm = betweenness_normalizado(grafo_atores, v)
                conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de intermediação mostra quais atores/atrizes são mais importantes como pontes entre outros pares da rede.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_5.txt", conteudo)

        elif opcao == "6":
            conteudo = "\n--- CENTRALIDADE DE PROXIMIDADE - ATORES ---\n"
            centralidade = closeness_centrality(grafo_atores)
            conteudo += "Top 10 atores/atrizes com maior proximidade:\n"
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                norm = closeness_normalizado(grafo_atores, v)
                conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de proximidade indica quais atores têm menor distância média até todos os outros.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_6.txt", conteudo)

        elif opcao == "7":
            conteudo = "\n--- CENTRALIDADE DE GRAU - DIRETORES (ENTRADA) ---\n"
            graus = degree_centrality(grafo_direcional, mode="in")
            conteudo += "Top 10 diretores com maior grau de entrada:\n"
            for v, g in sorted(graus.items(), key=lambda x: -x[1])[:10]:
                norm = grau_normalizado(grafo_direcional, v, mode="in")
                conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de grau (entrada) indica quantos atores diferentes trabalharam com cada diretor.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_7.txt", conteudo)

        elif opcao == "8":
            conteudo = "\n--- CENTRALIDADE DE INTERMEDIAÇÃO - DIRETORES ---\n"
            centralidade = betweenness_centrality(grafo_direcional)
            conteudo += "Top 10 diretores com maior intermediação:\n"
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                norm = betweenness_normalizado(grafo_direcional, v)
                conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de intermediação no grafo direcionado indica quais diretores são mais relevantes como intermediários nos caminhos mais curtos.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_8.txt", conteudo)

        elif opcao == "9":
            conteudo = "\n--- CENTRALIDADE DE PROXIMIDADE - DIRETORES ---\n"
            centralidade = closeness_centrality(grafo_direcional)
            conteudo += "Top 10 diretores com maior proximidade:\n"
            for v, c in sorted(centralidade.items(), key=lambda x: -x[1])[:10]:
                norm = closeness_normalizado(grafo_direcional, v)
                conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"
            conteudo += "\n👉 A centralidade de proximidade mostra os diretores mais próximos de todos os outros na rede.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_9.txt", conteudo)
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
