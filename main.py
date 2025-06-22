import os
import platform
from collections import defaultdict
from grafo import carregar_dados_padronizados, construir_grafo_participantes
from algoritmos import (
    componentes_conexas,
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

def mostrar_menu(tipo_grafo):
    print("""
===== ANÁLISE DE REDES COMPLEXAS =====
1. Informações básicas do grafo
2. Componentes conexas
""" + ("3. Árvore Geradora Mínima (apenas para atores)\n" if tipo_grafo == 'atores' else "") +
    ("4. Centralidade de Grau\n" if tipo_grafo != 'direcional' else "4. Centralidade de Grau (in/out)\n") +
    "3. Centralidade de Intermediação\n" +
    "6. Centralidade de Proximidade\n" +
    "0. Sair\n======================================\n")
    return input("Escolha uma opção: ").strip()

def executar_opcao(opcao, grafo, tipo_grafo):
    conteudo = ""

    if opcao == "1":
        v, a = grafo.obter_info()
        conteudo += f"\n--- INFORMAÇÕES BÁSICAS DO GRAFO ---\n"
        conteudo += f"Grafo de {tipo_grafo}: {v} vértices, {a} arestas\n"

    elif opcao == "2":
        comp = componentes_conexas(grafo)
        conteudo += f"\n--- COMPONENTES CONEXAS ---\n"
        conteudo += f"Grafo de {tipo_grafo}: {len(comp)} componentes conexas\n"

    elif opcao == "3" and tipo_grafo == 'atores':
        conteudo += "\n--- ÁRVORE GERADORA MÍNIMA (PRIM) ---\n"
        print("1 - Informar vértice manualmente")
        print("2 - Escolher automaticamente o primeiro vértice disponível")
        escolha = input("Opção (1 ou 2): ").strip()

        if escolha == "1":
            raiz = input("Informe o nome do vértice inicial: ").strip().upper()
            if raiz not in grafo.vertices:
                conteudo += f"Vértice '{raiz}' não encontrado.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                return
        elif escolha == "2":
            if not grafo.vertices:
                conteudo += "O grafo está vazio.\n"
                print(conteudo)
                salvar_em_txt("saida_opcao_3.txt", conteudo)
                return
            raiz = next(iter(grafo.vertices))
            conteudo += f"Raiz escolhida automaticamente: {raiz}\n"
        else:
            conteudo += "Opção inválida.\n"
            print(conteudo)
            salvar_em_txt("saida_opcao_3.txt", conteudo)
            return

        agm, custo = agm_prim(grafo, raiz)
        if not agm:
            conteudo += "Não foi possível gerar a AGM. Verifique se o grafo é conexo.\n"
        else:
            conteudo += f"\nCusto total da AGM: {custo}\n"
            salvar_agm_completa_em_txt(agm, raiz)

    elif opcao == "4":
        conteudo += f"\n--- CENTRALIDADE DE GRAU - {tipo_grafo.upper()} ---\n"
        if tipo_grafo == 'direcional':
            graus_in = degree_centrality(grafo, mode="in", normalizar=True)
            graus_out = degree_centrality(grafo, mode="out", normalizar=True)
            conteudo += "Top 10 por grau de entrada (in):\n"
            for v, (g, norm) in sorted(graus_in.items(), key=lambda x: -x[1][0])[:10]:
                conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"
            conteudo += "\nTop 10 por grau de saída (out):\n"
            for v, (g, norm) in sorted(graus_out.items(), key=lambda x: -x[1][0])[:10]:
                conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"
        else:
            graus = degree_centrality(grafo, normalizar=True)
            for v, (g, norm) in sorted(graus.items(), key=lambda x: -x[1][0])[:10]:
                conteudo += f"{v}: {g} (normalizado: {norm:.4f})\n"

    elif opcao == "5":
        conteudo += f"\n--- CENTRALIDADE DE INTERMEDIAÇÃO - {tipo_grafo.upper()} ---\n"
        centralidade = betweenness_centrality(grafo, normalizar=True)
        for v, (c, norm) in sorted(centralidade.items(), key=lambda x: -x[1][0])[:10]:
            conteudo += f"{v}: {c:.4f} (normalizado: {norm:.4f})\n"

    elif opcao == "6":
        print(f"\n--- CENTRALIDADE DE PROXIMIDADE (CLOSENESS) - {tipo_grafo.upper()} ---")
        componentes = componentes_conexas(grafo)
        maior_componente = max(componentes, key=len)
        centralidade = closeness_centrality(grafo, vertices=maior_componente)
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

    elif opcao == "0":
        print("Saindo do programa... Até mais!")
        exit()

    else:
        print("Opção inválida.\n")
        return

    if conteudo:
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

    print("Escolha o tipo de grafo para análise:")
    print("1 - Grafo de atores (não direcionado)")
    print("2 - Grafo de diretores (não direcionado, ligação por atores em comum)")
    print("3 - Grafo direcionado (atores → diretores)")
    escolha = input("Opção (1, 2 ou 3): ").strip()

    if escolha == "1":
        tipo_grafo = 'atores'
        grafo = construir_grafo_participantes(elencos, diretores, tipo=tipo_grafo)
    elif escolha == "2":
        tipo_grafo = 'diretores'
        grafo = construir_grafo_participantes(elencos, diretores, tipo=tipo_grafo)
    elif escolha == "3":
        tipo_grafo = 'direcional'
        from grafo import construir_grafo_direcional
        grafo = construir_grafo_direcional(elencos, diretores)
    else:
        print("Opção inválida. Encerrando.")
        return

    print(f"Grafo de {tipo_grafo} criado com sucesso!")

    while True:
        opcao = mostrar_menu(tipo_grafo)
        executar_opcao(opcao, grafo, tipo_grafo)
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
