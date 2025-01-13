from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

import re
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it
import numpy as np
import os
import json
import io
from PIL import Image

Builder.load_file('front-end.kv')
def diretorio(nomeArquivo):
    diretorioAtual = os.path.dirname(__file__)
    diretorioArquivo = os.path.join(diretorioAtual, nomeArquivo + ".json")
    return diretorioArquivo

def diretorioImagem(nomeArquivo):
    diretorioAtual = os.path.dirname(__file__)
    diretorioArquivo = os.path.join(diretorioAtual, nomeArquivo + ".png")
    return diretorioArquivo

def criacaoArquivo(parametrosEstados, nomeArquivo):
    arquivo = open(diretorio(nomeArquivo), "w")
    json.dump(parametrosEstados, arquivo)
    arquivo.close()

def leituraArquivo(nomeArquivo):
    arquivo = open(diretorio(nomeArquivo), "r")
    return json.load(arquivo)

def geraTransicoes(estados):
    for i in range(estados):  # geração dos estados conforme a entrada da quantidade
        if i == 0:
            estadosGerados = "q{}".format(i)
        else:
            estadosGerados += ",q{}".format(i)
    estadosGerados = estadosGerados.split(',')  # dividindo os estados que foram gerados
    return estadosGerados


# Função que realiza a ordenação de estados
def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))  # retorna a lista ordenada pelo número dentro da string


# Função para ordenar os estados
def ordenado(string):
    teste = string.split(', ')  # transformando a string em lista para fazer a ordenação
    teste.sort(
        key=num_sort)  # chamada da função da realização de ordenação de estados para ordenar pelo número do estado na string
    concatenacao = ''
    i = 0
    while i < len(
            teste):  # loop para concatenar os elementos da string que foram separados em uma lista para string novamente
        if concatenacao == '':
            concatenacao = teste[i]
        else:
            concatenacao = concatenacao + ', ' + teste[i]
        i += 1

    return concatenacao


# Função recursiva para a realização da conversão
def conversao(conjTransicoes, transicoesConvertidas, alfabeto, ultimoAdicionado):
    ultimoAlternativo = ordenado(
        ultimoAdicionado)  # atribuição de conjunto de estados ordenado para o último que foi adicionado na função de transição que está sendo convertida
    # print(ultimoAlternativo)

    for transicoes in transicoesConvertidas:  # loop para verificar se de todas as transições possíveis, há aquelas que não são transições vazias ou que não levam a uma transição(transições inúteis)
        if ultimoAlternativo == transicoes[
            0]:  # verifica se o último adicionado nas transições que não são inúteis leva a uma outra transição não inútil
            transicoes[2] = ordenado(
                transicoes[2])  # chama a função de ordenação de string para ordenar o estado resultante
            conjTransicoes.append(transicoes)  # adiciona a função de transição não inútil
            jaAdicionou = False  # variável para controle de transições que já foram (ou não) adicionadas para caso haja transição que leva para o próprio estado
            for transicoes1 in conjTransicoes:  # loop para verificar se já foi adicionado transições que levam para o próprio estado
                if transicoes1[0] == transicoes[2]:
                    jaAdicionou = True
            if not jaAdicionou:
                if ultimoAlternativo != transicoes[2]:
                    conversao(conjTransicoes, transicoesConvertidas, alfabeto, transicoes[
                        2])  # chamada recursiva com o último estado resultante adicionado para verificar se há outro estado que não seja inútil
    # print(conjTransicoes)
    return conjTransicoes  # após a adição de todos estados não inúteis, retorna o conjunto de transições que possui estados não inúteis


# Conversão de AFN para AFD
def conversaoAFN(parametrosEstados):
    estadosGerados = parametrosEstados[3].copy()  # realiza uma cópia do conjunto de transições que foi gerado inicialmente
    transicoesConvertidas = []
    estados = parametrosEstados[3].copy()  # realiza uma cópia para servir de variável auxiliar na concatenação

    atualizarIndice = 0  # variável auxiliar para atualizar o índice da lista de estados que foram gerados e poder por meio dela fazer as concatenações
    vezes = (2 ** len(
        estadosGerados)) - 1  # conceito de produção das concatenações de estados da conversão em que matematicamente seria 2 elevado a quantidade de estados menos o estado vazio (...- 1)
    i = 0
    k = 0
    j = 0

    while i < vezes:  # loop para realizar as concatenações
        teste = estadosGerados[atualizarIndice].split(
            ', ')  # transformação da "string" com os estados em uma lista para que passe por cada estado existente
        ultimoIndiceTeste = len(
            teste) - 1  # variável que pega o último índice do estado concatenado que foi adicionado para que por meio dele, seja adicionados os outros que serão concatenados, podendo ser feita uma espécie de agrupamento
        j = 0
        indiceEstado = 0  # variável auxiliar para indicar onde está o estado na qual possui o último estado concatenado (ou agrupado)
        while j < len(estados):  # loop para achar o estado que foi último a ser agrupado
            if estados[j] == teste[ultimoIndiceTeste]:
                indiceEstado = j
            j += 1
        k = indiceEstado + 1  # variável que recebe o índice do último estado que foi agrupado e que servirá para procurar outros estados restantes que não foram agrupados
        while k < len(estados):  # loop para agrupar outros estados restantes
            estadosGerados.append(estadosGerados[atualizarIndice] + ', ' + estados[
                k])  # adiciona a uma das cópias dos estados existentes, o estado concatenado que também servirá para adicionar estados concatenados dos estados concatenados
            k += 1
        i += 1

        if atualizarIndice != len(
                estadosGerados) - 1:  # assim que foram feitas todas as concatenações possíveis com o estado que está em evidência para armazenar sua concatenação, é verificado se não atingiu o fim da lista de estados concatenados
            atualizarIndice += 1
    # print(estadosGerados)
    conjEstados = []
    for alfabeto in parametrosEstados[1]:  # loop auxiliar de controle que passa por todos símbolos do alfabeto
        i = 0
        while i < len(estadosGerados):  # loop auxiliar que passa por todos os estados concatenados
            conversoesInicial = ''  # variável auxiliar que servirá para concatenação dos estados de ativação da função de transição
            conversoesFinal = ''  # variável auxiliar que servirá para concatenação dos estados resultantes da função de transição
            teste = estadosGerados[i].split(', ')  # variável que divide a concatenação dos estados concatenados
            j = 0
            contagem = 0  # variável auxiliar que indica se houve o armazenamento da primeira parte do estado concatenado
            while j < len(teste):  # loop que passa pela divisão dos estados concatenados
                for transicoes in parametrosEstados[
                    4]:  # loop que passa por todas as transições para achar a função de transição que corresponde à parte atual do estado concatenado
                    if teste[j] == transicoes[0] and alfabeto == transicoes[
                        1] and contagem == 0:  # verifica se os estado de ativação e a parte do estado concatenado coincidem e se na função de transição se trata de apenas um símbolo na qual está no momento atual do loop do alfabeto e se trata-se da primeira parte a ser adicionada
                        conversoesInicial = transicoes[0]
                        conversoesFinal = transicoes[2]
                        contagem += 1
                    elif teste[j] == transicoes[0] and alfabeto == transicoes[
                        1] and contagem != 0:  # se não for a primeira parte a ser adicionada, faz-se apenas a concatenação

                        if teste[
                            j] not in conversoesInicial:  # verifica se já não foi adicionada a parte atual do estado concatenado
                            conversoesInicial = conversoesInicial + ', ' + transicoes[0]
                            if transicoes[
                                2] not in conversoesFinal:  # verifica se estado resultante da função de transição já não foi adicionado
                                conversoesFinal = conversoesFinal + ', ' + transicoes[2]
                            else:  # se já foi adicionado, apenas atribui
                                conversoesFinal = transicoes[2]
                        else:  # se já foi adicionado, apenas atribui (sem concatenar)
                            conversoesInicial = transicoes[0]
                            if transicoes[2] not in conversoesFinal:
                                conversoesFinal = conversoesFinal + ', ' + transicoes[2]
                            else:
                                conversoesFinal = transicoes[2]
                j += 1
            i += 1
            transicoesConvertidas.append([conversoesInicial, alfabeto,
                                          conversoesFinal])  # adiciona as transições que foram concatenadas em outra variável

    # print(transicoesConvertidas)

    conjTransicoes = []
    for alfabeto in parametrosEstados[1]:
        i = 0
        while i < len(transicoesConvertidas):
            if parametrosEstados[0] == transicoesConvertidas[i][0] and alfabeto == transicoesConvertidas[i][1]:
                transicoesConvertidas[i][2] = ordenado(transicoesConvertidas[i][2])
                conjTransicoes.append(transicoesConvertidas[
                                          i])  # adiciona o primeiro estado de ativação da função de transição para quaisquer símbolos que exista no alfabeto, este que servirá de guia para eliminar os estados inúteis
            i += 1

    indice = len(
        conjTransicoes)  # variável que armazena a última função de transição com o último símbolo possível em relação estados iniciais de ativação da função de transição
    i = 0
    while i < indice:  # loop com a chamada da função recursiva que passará por todos estados úteis
        conjTransicoes = conversao(conjTransicoes, transicoesConvertidas, parametrosEstados[1], conjTransicoes[i][2])
        i += 1
    # print(conjTransicoes)

    i = 0
    while i < len(conjTransicoes):  # loop para remoção de funções de transição repetidas
        j = i + 1
        while j < len(conjTransicoes):  # loop auxiliar para fazer comparação
            if conjTransicoes[i][0] == conjTransicoes[j][0] and conjTransicoes[i][1] == conjTransicoes[j][
                1]:  # verifica se o estado de ativação da função coincide e possuem o mesmo símbolo, efetuando a remoção
                conjTransicoes.remove(conjTransicoes[j])
                i -= 1  # ação que mantém o índice atual da função de transição
            j += 1
        i += 1
    # print(conjTransicoes)

    estadoNovo = 'F'
    transicoesPont = conjTransicoes  # variável que serve como ponteiro para o "conjunto" de funções de transição

    for transicoes in conjTransicoes:  # loop para verificar se possui alguma função de transição que leva à transição nula (transição vazia) "eliminando" a transição vazia dando lugar a um estado de rejeição
        destino = transicoes[2].split(
            ', ')  # efetua a separação da concatenação do estado resultante para verificar se há um "estado vazio"
        resultado = ''
        indice = 0
        for d in destino:  # loop para passar sobre todos os estados concatenados que foram separados
            if d == '':  # verifica se já no primeiro estado separado é vazio, se sim, atribui um estado novo
                d = estadoNovo
            if indice == 0:  # verifica se trata-se da primeira parte do estado concatenado separado, atribuindo-o
                resultado = d
            else:  # se não, apenas concatena
                resultado = resultado + ', ' + d
            indice += 1
        transicoes[2] = resultado  # atribui à transição que há "estado vazio" o estado novo (estado de rejeição)

    novoEstado = False  # variável que libera (ou não) a inclusão do estado de rejeição como um dos estados que faz parte do conjunto de estados
    for j in conjTransicoes:  # loop para verificar se foi incluído o estado de rejeição na transição vazia
        if estadoNovo in j[2]:
            novoEstado = True

    if novoEstado:  # se foi incluído na transição vazia, inclui as funções de transição em relação a cada simbolo para o estado de rejeição
        for alfabeto in parametrosEstados[1]:
            transicoesPont.append([estadoNovo, alfabeto, estadoNovo])

    for alfabeto in parametrosEstados[1]:
        for transicoes in conjTransicoes:
            if transicoes[
                1] == alfabeto:  # verificação por meio de loops auxiliares de transição e do símbolos do alfabeto para armazenar os estados que compõem o conjunto de estados depois que foram convertidos
                conjEstados.append(transicoes[0])
    conjEstados.append(parametrosEstados[0])
    copia = set(
        conjEstados)  # variável que "converte" o conjunto de estados do tipo lista para o tipo set, pois o tipo set é um tipo de lista que não admite duplicações, portanto, eliminando quaisquer tipo de duplicações de estados
    conjEstados = list(copia)  # convertendo de volta os estados
    # print(conjEstados)

    # print(conjTransicoes)

    return minimizacao(parametrosEstados, conjTransicoes,
                       conjEstados)  # retorno com a chamada da função de minimização que também retornará as transições minimizadas


# Minimização do autômato convertido para AFD
def minimizacao(parametrosEstados, conjTransicoes, conjEstados):
    conjEstIniciais = []
    conjEstFinais = []
    estadoInicial = parametrosEstados[0]

    for estados in conjEstados:  # loop para verificar quais estados do conjunto de estados é(são) final(is)
        for finais in parametrosEstados[2]:  # loop para passar pelo(s) estado(s) final(is)
            if finais in estados:  # verifica se o estado atual do conjunto de estados é final
                conjEstFinais.append(estados)  # armazena no conjunto de estados finais
    copia = set(conjEstFinais)  # conversão para retirada de duplicados
    conjEstFinais = list(copia)  # conversão de volta
    # print(conjEstFinais)

    i = 0
    while i < len(conjEstados):  # loop para verificar quais estados são não-finais
        final = False  # variável para delimitar o armazenamento de estados não-finais
        for finais in parametrosEstados[2]:
            if finais in conjEstados[
                i]:  # se algum dos estados forem finais, delimita o armazenamento mudando a variável para True
                final = True
        if not final:  # verifica se é um estado final, se não, armazena.
            conjEstIniciais.append(conjEstados[i])
        i += 1
    estadosSemRepeticao = set(conjEstIniciais)
    conjEstIniciais = list(estadosSemRepeticao)
    # print(conjEstIniciais)

    pares = []
    transicoesCopia = conjTransicoes  # variável que recebe a cópia do conjunto de transições que veio como parametro

    indice = 0  # variável que servirá para marcar a posição do par no conjunto de pares que farão a verificação de minimização
    i = 0
    while i < len(conjEstIniciais):  # loop para fazer os pares dos estados não-finais
        j = i + 1
        while j < len(conjEstIniciais):  # loop auxiliar para seja feita pares diferentes
            if conjEstIniciais[i] != conjEstIniciais[j]:  # verifica se os pares são diferentes
                indice += 1
                pares.append([conjEstIniciais[i], conjEstIniciais[j], False,
                              indice])  # adiciona os pares diferentes, com uma "variável" que servirá para caso seja True não haja a fusão dos estados e False para que haja a fusão de estados, além do índice que marca a posição do par
            j += 1
        i += 1

    i = 0
    while i < len(conjEstFinais):  # loop para fazer os pares de estados finais
        j = i + 1
        while j < len(conjEstFinais):  # loop auxiliar para que seja feita para pares finais diferentes
            if conjEstFinais[i] != conjEstFinais[j]:  # verifica se são pares diferentes
                indice += 1
                pares.append([conjEstFinais[i], conjEstFinais[j], False,
                              indice])  # adiciona os pares diferentes, com uma variável False que poderá ser modificada caso não seja necessária uma fusão(True) e o índice
            j += 1
        i += 1

    # print(pares)

    for par in pares:  # loop para que passe por todos os pares e verifique a possibilidade de fusão ou não
        pares = minimizar(par[3] - 1, -1, pares, conjTransicoes, parametrosEstados[1], parametrosEstados[
            2])  # função recursiva que verifica cada par, com o seu respectivo índice, o índice anterior ao atual(inicializado com -1), os pares, as funções de transições convertidas, o alfabeto e os estados finais de antes da conversão

    # print(pares)

    for i in pares:  # loop para verificar quais pares foram "marcados" com False
        for alfabeto in parametrosEstados[1]:  # loop para controle sob quais simbolos farão a alteração
            for transicoes in transicoesCopia:  # loop para controle sob quais transições que farão a alteração
                if not i[2]:  # verifica se o par foi "marcado" com False, assim fazendo a fusão de transições
                    if transicoes[0] == i[0] and alfabeto == transicoes[
                        1]:  # verifica se um dos pares é compatível com a transição e o simbolo correspondente ao loop de controle
                        # print(transicoes[0] + ', ' + i[0])
                        for t in transicoesCopia:  # loop para verificar o outro par
                            if t[0] == i[1] and alfabeto == t[
                                1]:  # verifica se o outro par é compatível com a transição e o simbolo correspondente ao loop de controle
                                if estadoInicial == t[0] or estadoInicial == transicoes[0]:
                                    estadoInicial = i[0] + ', ' + i[1]
                                transicoesCopia.append([i[0] + ', ' + i[1], alfabeto, transicoes[2] + ', ' + t[
                                    2]])  # adiciona a transição com os pares fundidos
                                transicoesCopia.remove(
                                    t)  # remove a transição de um dos pares que fizeram fusão, dando lugar aos pares fundidos
                                transicoesCopia.remove(transicoes)  # remove a transição do outro par

    estado = estadoInicial.split(', ')
    i = 0
    while i < len(estado):
        removeu = False
        j = i + 1
        while j < len(estado):
            if estado[i] == estado[j]:
                estado.remove(estado[j])
                removeu = True
            j += 1
        if not removeu:
            i += 1

    estadoInicial = ''
    i = 0
    while i < len(estado):
        if estadoInicial == '':
            estadoInicial = estado[i]
        else:
            estadoInicial = estadoInicial + ', ' + estado[i]
        i += 1

    # print(transicoesCopia)
    for transicoes in transicoesCopia:  # loop que passará por todas as transições e verificará se ha alguma transição fundida com estado de ativação e estado resultante de "mesmo nome"
        entradaSRepeticao = ''  # variável que servirá para concatenação do estado de ativação que será separado
        saidaSRepeticao = ''  # variável que servirá para concatenação do estado resultante que será separado
        entrada = transicoes[0].split(', ')  # separação do estado de ativação para fazer a comparação
        saida = transicoes[2].split(', ')  # separação do estado resultante para fazer a comparação
        i = 0
        while i < len(
                entrada):  # loop do estado de ativação separado da transição atual passando por cada estado separado
            j = i + 1
            removeu = False  # variável de controle para efetuar a mudança de índice na remoção do estado repetido
            while j < len(entrada):  # loop auxiliar para fazer a comparação
                if entrada[i] == entrada[j]:  # verifica se no estado de ativação há um estado igual
                    entrada.remove(entrada[j])  # remove um dos iguais
                    removeu = True
                j += 1
            if not removeu:  # verifica se foi removido para manter o índice do que está verificando e poder remover mais repetições
                i += 1

        i = 0
        while i < len(entrada):  # loop para fazer a concatenação novamente do estado de ativação que foi separado
            if entradaSRepeticao == '':
                entradaSRepeticao = entrada[i]
            else:
                entradaSRepeticao = entradaSRepeticao + ', ' + entrada[i]
            i += 1
        # print(entradaSRepeticao)
        transicoes[
            0] = entradaSRepeticao  # armazena no estado de ativação da função de transição atual o estado sem repetições

        i = 0
        while i < len(
                saida):  # loop de cada estado resultante que foi separado da transição atual passando por cada estado resultante separado
            removeu = False
            j = i + 1
            # print(saida[i])
            while j < len(saida):  # loop auxiliar para comparação de cada estado resultante separado
                if saida[i] == saida[j]:  # verifica se no estado resultante, há um outro igual
                    saida.remove(saida[j])  # remove o estado igual
                    removeu = True
                j += 1
            if not removeu:  # verificando se foi removido para manter o índice do estado que está sendo verificado se há repetição
                i += 1

        i = 0
        while i < len(saida):  # loop para concatenação do estado resultante que foi separado da transição atual
            if saidaSRepeticao == '':
                saidaSRepeticao = saida[i]
            else:
                saidaSRepeticao = saidaSRepeticao + ', ' + saida[i]
            i += 1
        # print(saidaSRepeticao)
        transicoes[
            2] = saidaSRepeticao  # armazena no estado resultante da função de transição atual o estado sem repetições
    # print(transicoesCopia)

    for alfabeto in parametrosEstados[1]:  # loop de controle passando por cada elemento do alfabeto
        for transicoes in transicoesCopia:  # loop passando por cada transição para verificar se há alguma função com transição a um estado inexistente
            achou = False  # variável de controle para verificar se a transição atual possui transição existente
            for t in transicoesCopia:  # loop auxiliar que achará a transição existente (ou não)
                if transicoes[2] == t[
                    0]:  # se possuir uma transição existente para a atual, altera a variável de controle
                    achou = True

            if not achou:  # se a variável de controle não foi alterada, não possui transição existente, assim sendo alterada o estado resultante para o próprio estado
                transicoes[2] = transicoes[0]

    estadoFinal = []
    for transicoes in transicoesCopia:  # loop para pegar todos os estados finais que foram convertidos e minimizados
        for finais in parametrosEstados[
            2]:  # loop que passa pelos estados finais antes da conversão e minimização para marcar os estados finais e "atualizar"
            if finais in transicoes[0]:  # verifica se o estado de ativação é um estado final
                estadoFinal.append(transicoes[0])  # armazena os estados finais

    estadosGerados = []
    for alfabeto in parametrosEstados[1]:  # loop de controle passando por cada elemento do alfabeto
        for transicoes in transicoesCopia:  # loop que passa por todas as funções de transição
            if alfabeto == transicoes[1]:  # verifica se o símbolo corresponde ao símbolo da função de transição
                estadosGerados.append(transicoes[
                                          0])  # armazena os estados de ativação das funções de transição, pois estes serão os novos estados
    estadosCopia = set(estadosGerados)  # remove estados repetidos convertendo para o tipo set
    estadosGerados = list(estadosCopia)  # converte de volta para o tipo lista'

    ambiguidade = []
    for estados in estadosGerados:  # loop passando por todos novos estados que foram armazenados fazendo a criação do novo parametro "ambiguidade" assim, sem que haja alguma ambiguidade, pois os estados foram minimizados
        for alfabeto in parametrosEstados[1]:
            ambiguidade.append([estados, alfabeto, 0])

            # print(estadosGerados)
    # print(estadoFinal)
    # print(transicoesCopia)

    return estadoInicial, parametrosEstados[1], estadoFinal, estadosGerados, transicoesCopia, len(
        estadosGerados), ambiguidade  # retorna todos os parametros necessarios para a simulação, sendo eles: o estado inicial (que não muda), o alfabeto, o estado final (depois da minimização), o conjunto de estados (depois da minimização), as transições minimizadas, quantidade de estados e o conjunto de ambiguidades (para controle na simulação)


def minimizar(indice, indiceAnterior, pares, conjTransicoes, alfabeto, estadoFinal):
    resultado = []
    achou = False  # variável de controle para caso não ache o par que ficou para ser marcado, marque o par que está fazendo a verificação de marcação (pois este corresponde aos pares já "marcados")

    # print(pares[indice])

    for simbolo in alfabeto:  # loop de controle para verificação de qual símbolo que se trata
        for estado1 in conjTransicoes:  # loop para encontrar o estado de ativação que corresponde ao primeiro par
            for estado2 in conjTransicoes:  # loop para encontrar o estado de ativação que corresponde ao segundo par
                if estado1[0] == pares[indice][0] and estado2[0] == pares[indice][1] and estado1[1] == simbolo and \
                        estado2[
                            1] == simbolo:  # verifica se os pares de cada loop corresponde ao par que foi gerado para verificar a possibilidade de minimizar e verifica se os dois se tratam do mesmo símbolo
                    resultado.append([estado1[2], estado2[
                        2]])  # armazena o estados resultantes de cada par e para cada símbolo, dependo do símbolo atual que corresponde ao loop do alfabeto
                    break
    # print(resultado)
    contagem = 0
    for r in resultado:  # loop que passa pelos outros pares formados pelos estados resultantes dos pares iniciais
        for par in pares:  # loop que passa pelos pares iniciais e verifica se os pares resultantes estão dentro dos pares iniciais (onde os pares iniciais são os pares a serem "marcados")
            if (r[0] == par[0] and r[1] == par[1]) or (r[0] == par[1] and r[1] == par[
                0]):  # verifica se o par resultante corresponde a um dos pares iniciais
                # print(r)
                if indice != indiceAnterior:  # verifica se o índice do par atual já foi verificado e que o par resultante corresponde ao próprio par inicial
                    pares = minimizar(par[3] - 1, indice, pares, conjTransicoes, alfabeto,
                                      estadoFinal)  # chamada recursiva para o par achado com o índice do par atual para verificar se acha os pares dos resultados e, assim, sucessivamente

    contagem = 0
    for r in resultado:  # loop para verificar os pares de resultados, se um ou mais pares levam é um mesmo estado e/ou é um estado final (este loop é exclusivo para caso há um par resultante que contém dentro dos pares iniciais ficando num "loop" com estes dois pares)
        if r[0] == r[1]:  # verifica se o par resultante são o mesmo estado
            contagem += 1
        else:
            for par in pares:  # loop para conferir se o par que não é igual, está no conjunto de pares, se sim, marca o par com a alteração da variável controle "achou", na qual, achou sendo True seria o par que não pode fundir
                if (r[0] == par[0] and r[1] == par[1]) or (r[0] == par[1] and r[1] == par[0]):
                    if contagem > 0:
                        achou = True

    if not achou and contagem < len(
            resultado):  # se a variável de controle deu falso é porque possui um par "marcado" seja porque foi marcado por se trata de pares que levam um ao outro ou por não estar na lista de pares para serem marcados, ou seja, um par já marcado e se os pares resultantes não forem todos estados iguais
        pares[indice][2] = True  # "marca o par"
    return pares  # retorno do conjunto de pares com a "marcação" (ou não) do par


def desenhar_grafo(grafo, nome_atributo, final):
    estiloConexao = [f"arc3,rad={r}" for r in it.accumulate([0.1] * 4)]

    pos = nx.planar_layout(grafo)
    nx.draw_networkx_nodes(grafo, pos, node_color='white', edgecolors='black', linewidths=2, node_size=1000)
    nx.draw_networkx_nodes(grafo, pos, nodelist=final, node_color='white', edgecolors='black', linewidths=2,
                           node_size=500)
    nx.draw_networkx_labels(grafo, pos, font_size=10)
    nx.draw_networkx_edges(
        grafo, pos, edge_color="black", connectionstyle=estiloConexao, min_target_margin=20
    )

    labels = {
        tuple(edge): f"{atributos[nome_atributo]}"
        for *edge, atributos in grafo.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        grafo,
        pos,
        labels,
        connectionstyle=estiloConexao,
        font_color="black",
        bbox={"alpha": 1, "facecolor": 'white', "edgecolor": 'white', 'boxstyle': 'square, pad=0'},
    )


def criarGrafo(parametrosEstados, nomearquivo):
    transicoes = parametrosEstados[4]
    fig, eixo = plt.subplots(1, 1)
    grafo = nx.MultiDiGraph()

    for t in transicoes:
        grafo.add_edge(t[0], t[2], alfabeto=t[1])
    desenhar_grafo(grafo, 'alfabeto', parametrosEstados[2])

    fig.tight_layout()
    plt.savefig(diretorioImagem(nomearquivo), format='png')
    plt.close()


class Telas(ScreenManager):
    pass

class Cadastro1(Screen):
    arquivo = []
    def on_enter(self, *args):
        self.manager.get_screen('cadastro1').ids.entrada.focus = True
    def validarEstado(self):
        if not self.manager.get_screen('cadastro1').ids.entrada.text.isdecimal():
            self.manager.get_screen('cadastro1').ids.aviso1.text = 'Entrada Inválida'
            self.manager.get_screen('cadastro1').ids.entrada.focus = True
            self.manager.get_screen('cadastro1').ids.entrada.text = ''
            return False
        else:
            self.manager.get_screen('cadastro1').ids.aviso1.text = ''
            self.manager.get_screen('cadastro1').ids.alfabeto.focus = True
            return True

    def validarAlfabeto(self):
        if self.manager.get_screen('cadastro1').ids.alfabeto.text == '':
            self.manager.get_screen('cadastro1').ids.aviso2.text = 'Entrada Inválida'
            self.manager.get_screen('cadastro1').ids.alfabeto.text = ''
            self.validarEstado()
        else:
            if ", " in self.manager.get_screen('cadastro1').ids.alfabeto.text:
                self.manager.get_screen('cadastro1').ids.aviso2.text = ''
                if self.validarEstado():
                    self.manager.current = 'cadastro2'
                    self.arquivo.append(self.manager.get_screen('cadastro1').ids.alfabeto.text.split(', '))
                    self.arquivo.append(geraTransicoes(int(self.manager.get_screen('cadastro1').ids.entrada.text)))
                    self.arquivo.append(int(self.manager.get_screen('cadastro1').ids.entrada.text))
                    criacaoArquivo(self.arquivo, "automato")
            else:
                self.manager.get_screen('cadastro1').ids.aviso2.text = 'Separe o alfabeto por virgula e espaço. Ex: f, g'


class Cadastro2(Screen):
    arquivo = None
    estados = []
    alfabeto = ''
    i = 0
    j = 0
    def on_enter(self, *args):
        self.arquivo = leituraArquivo("automato")
        #print(self.j)
        self.estados = self.arquivo[1]
        self.alfabeto = self.arquivo[0]
        self.manager.get_screen('cadastro2').ids.transicoes.text = f'Quantas transições existem para o estado {self.estados[self.i]} quando a entrada for {self.alfabeto[self.j]}?'
        self.manager.get_screen('cadastro2').ids.entrada.text = ''
        self.manager.get_screen('cadastro2').ids.entrada.focus = True

    def get_position(self):
        return self.i

    def get_alphabet(self):
        return self.j

    def set_alphabet(self, proximo):
        self.j = proximo

    def set_position(self, posicao):
        self.i = posicao

class Cadastro3(Screen):
    arquivo = None
    estados = None
    alfabeto = None
    i = Cadastro2.get_position(Cadastro2)
    j = Cadastro2.get_alphabet(Cadastro2)
    quantidade = 0
    transicoes = []
    ambiguidade = []
    def on_enter(self):
        self.arquivo = leituraArquivo('automato')
        self.estados = self.arquivo[1]
        self.alfabeto = self.arquivo[0]
        if int(self.manager.get_screen('cadastro2').ids.entrada.text) == 1:
            self.manager.get_screen('cadastro3').ids.definirtransicao.text = f'Para qual transição que o {self.estados[self.i]} quando a entrada for {self.alfabeto[self.j]}?'
        else:
            self.manager.get_screen(
                'cadastro3').ids.definirtransicao.text = f'Qual a {self.quantidade + 1}ª transição que o {self.estados[self.i]} quando a entrada for {self.alfabeto[self.j]}?'
        self.manager.get_screen('cadastro3').ids.selecao.text = f'{self.estados[0]}'
        self.manager.get_screen(
            'cadastro3').ids.selecao.values = self.definir()

    def definir(self):
        return self.estados

    def verificar(self):
        self.transicoes.append([self.estados[self.i], self.alfabeto[self.j], self.manager.get_screen('cadastro3').ids.selecao.text, self.quantidade + 1])
        final = False
        if self.quantidade < int(self.manager.get_screen('cadastro2').ids.entrada.text) - 1:
            self.quantidade += 1
        else:
            self.ambiguidade.append([self.estados[self.i], self.alfabeto[self.j], int(self.manager.get_screen('cadastro2').ids.entrada.text) - 1])
            self.quantidade = 0
            if len(self.alfabeto) - 1 > self.j:
                self.j += 1
            else:
                if len(self.estados) - 1 > self.i:
                    self.i += 1
                    self.j = 0
                else:
                    final = True

            if final:
                self.manager.current = 'cadastro4'
                self.arquivo.insert(2, self.transicoes)
                self.arquivo.append(self.ambiguidade)
                criacaoArquivo(self.arquivo, "automato")
            else:
                self.manager.current = 'cadastro2'
                Cadastro2.set_alphabet(Cadastro2, self.j)
                Cadastro2.set_position(Cadastro2, self.i)


        if int(self.manager.get_screen('cadastro2').ids.entrada.text) == 1:
            self.manager.get_screen('cadastro3').ids.definirtransicao.text = f'Para qual transição que o {self.estados[self.i]} quando a entrada for {self.alfabeto[self.j]}?'
        else:
            self.manager.get_screen(
                'cadastro3').ids.definirtransicao.text = f'Qual a {self.quantidade + 1}ª transição que o {self.estados[self.i]} quando a entrada for {self.alfabeto[self.j]}?'


    def position(self):
        return self.i

    def alphabet(self):
        return self.j

    def get_transicoes(self):
        return self.transicoes

class Cadastro4(Screen):
    estados = 0
    estadoInicial = ''
    arquivo = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self, *args):
        self.arquivo = leituraArquivo("automato")
        self.estados = self.arquivo[1]
        for e in self.estados:
            self.ids.caixa.add_widget(CheckBInicial(text=e))
    def returning(self):
        for i in self.ids.caixa.children:
            if i.get_valor():
                self.estadoInicial = i.ids.estado.text
        self.arquivo.insert(0, self.estadoInicial)
        criacaoArquivo(self.arquivo, 'automato')
        self.manager.current = 'cadastro5'

    def get_estado(self):
        return self.estadoInicial

class Cadastro5(Screen):
    estados = 0
    finais = []
    arquivo = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self, *args):
        self.arquivo = leituraArquivo('automato')
        self.estados = self.arquivo[2]
        for e in self.estados:
            self.ids.caixa.add_widget(CheckBFinal(text=e))
    def returning(self):
        for i in self.ids.caixa.children:
            if i.get_valor():
                self.finais.append(i.ids.estado.text)
        self.arquivo.insert(2, self.finais)
        criacaoArquivo(self.arquivo, 'automato')
        self.manager.current = 'menu'

    def get_finais(self):
        return self.finais

class CheckBFinal(BoxLayout):
    valor = False
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.ids.estado.text = text

    def checkbox(self, instance, value):
        if value == True:
            self.valor = True
        else:
            self.valor = False

    def get_valor(self):
        return self.valor


class CheckBInicial(BoxLayout):
    valor = False
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.ids.estado.text = text

    def checkbox(self, instance, value):
        if value == True:
            self.valor = True
        else:
            self.valor = False

    def get_valor(self):
        return self.valor


class Botao(ButtonBehavior, Label):
    cor = ListProperty([0, 0.2, 0.4, 1])
    cor2 = ListProperty([0.1, 0.1, 0.1, 1])

    def __init__(self, **kwargs):
        super(Botao, self).__init__(**kwargs)
        self.atualizar()

    def on_pos(self, *args):
        self.atualizar()

    def on_size(self, *args):
        self.atualizar()

    def on_press(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

    def on_release(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

    def on_cor(self, *args):
        self.atualizar()

    def atualizar(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.cor)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[40])


def simulacao(parametrosEstados,
              palavra):  # apenas um parametro para acessar as variáveis que retornaram, pois elas estão em formato de tuplas
    estadoAtual = parametrosEstados[
        0]  # a variável armazena o estado inicial conforme a posição que corresponde ao estado inicial para fazer o movimento entre estados
    estadoTemporario = []

    sinal = False  # variável para sinalizar se existe uma ambiguidade que é presente nos AFNs
    for i in palavra:  # loop para passar por cada simbolo da palavra que será testada
        for j in parametrosEstados[
            1]:  # loop para verificar se existe um simbolo na palavra que não faz parte do alfabeto
            if i == j:
                break
        else:  # condição para que caso haja algum simbolo que não faça parte do alfabeto, não fazendo a leitura dos simbolos
            print('Palavra rejeitada, pois ela não faz parte do alfabeto')
            break

        tamanho = 0
        while tamanho < len(
                estadoTemporario):  # loop para que quando houver alguma ambiguidade de estados resultantes poder retirar a sinalização de estado que foi adicionado recente
            estadoTemporario[tamanho][
                3] = False  # "variável" dentro da lista de estados que houveram ambiguidades para marcar que o estado não foi adicionado recentemente
            tamanho += 1
        ocorrencia = False  # variável que delimita se houve modificação no estado atual para AFD
        ambiguidades = 0
        entrou = False  # variável que delimita se foi feita alguma modificação na lista de estados que houveram ambiguidade
        contagem = 0  # variável que servirá para delimitar o armazenamento do resultante do estado que há ambiguidade
        entrada = 0  # variável que servirá para verificar se houve modificações para todos os estados que depararam com alguma ambiguidade e que foram armazenadas
        for k in parametrosEstados[
            4]:  # loop que passará por todas as funções de transição para achar o que corresponde ao simbolo atual e ao(s) estado(s) atual(is) que se encontra(m)
            for ambiguidade in parametrosEstados[
                6]:  # loop que passa por todos estados que foram armazenados baseando-se no estado atual da função de transição e retornando a quantidade de ambiguidade (0 ou mais)
                if not ocorrencia:  # verifica se continua sem modificação no estado atual
                    if k[0] == ambiguidade[0] and i == ambiguidade[1] and i == k[
                        1]:  # verifica se o estado de ativação da função possui ambiguidade e se também tanto o simbolo do estado de ativação quanto o simbolo que foi armazenado junto com as outras informações do estado são compatíveis com o simbolo que está sendo lido
                        ambiguidades = ambiguidade[
                            2]  # se compatível, armazena quantas ambiguidades o estado possui (0 ou mais)
            if k[0] == estadoAtual and i == k[
                1]:  # verifica se o estado de ativação é o estado atual de leitura e se o simbolo do estado de ativação é compatível com o simbolo de leitura atual
                if not ocorrencia and ambiguidades == 0:  # verifica se não houve a modificação para o estado atual e se não há ambiguidades para o estado "atual"
                    estadoAtual = k[
                        2]  # k[0] é o estado de ativação, k[1] é o símbolo, k[2] é o estado resultante e k[3] é a ocorrência para casos de haver ambiguidade
                    ocorrencia = True
                elif ambiguidades >= 1:  # se há mais de uma ambiguidade para o estado atual e ativa os estados atuais "paralelos"
                    if len(estadoTemporario) < ambiguidades + 1:  # verifica se ainda não adicionou todos os estados na qual houve a "ambiguidade"
                        if contagem < ambiguidades + 1:  # verifica se ainda pode armazenar mais uma função de transição ambígua
                            estadoTemporario.append([k[0], k[3], k[2],
                                                     True])  # armazenamento de uma parte da "maquina" com um dos estados que possuem ambiguidade com apenas o estado de ativação que houve ambiguidade, o indice de ocorrencia, o estado resultante e a variável que determina se ele foi armazenado recentemente, sendo 'True' como que armazenou recentemente
                            contagem += 1  # contagem de armazenamento de estados
                    else:
                        if estadoTemporario[len(estadoTemporario) - 1][0] != k[
                            0]:  # se adicionou todos os estados que houveram ambiguidade, verifica se o estado que houve ambiguidade já não foi armazenado
                            if contagem < ambiguidades + 1:
                                estadoTemporario.append([k[0], k[3], k[2], True])
                                # print(contagem)
                                contagem += 1
                    sinal = True

            if sinal and not entrou:  # por meio da variável "sinal" é liberado (ou não) as modificações no estados ambiguos e a variável "entrou" é para a modificação feita nos estados ambíguos
                if len(estadoTemporario) < 2:  # se existe apenas um estado que seja ambíguo, apenas sua modificação será feita
                    if k[0] == estadoTemporario[0][2] and i == k[1] and not estadoTemporario[0][
                        3]:  # verifica se o estado resultante é o mesmo do estado de ativação da função e o simbolo corresponde ao simbolo atual da palavra e também se o estado não foi adicionado recentemente
                        if k[0] != estadoTemporario[0][
                            0]:  # verifica se o estado de ativação não é o estado que houve a ambiguidade
                            estadoTemporario[0][2] = k[2]
                        else:
                            if estadoTemporario[0][1] == k[
                                3]:  # se for o estado que houve ambiguidade, verifica se o indice de ocorrência é compatível para seguir pelo "caminho" que foi definido
                                estadoTemporario[0][2] = k[2]
                        entrou = True  # modificação feita
                else:
                    h = 0
                    while h < len(
                            estadoTemporario):  # se existir mais de um estado ambíguo armazenado, passará por todos os estados armazenados
                        if k[0] == estadoTemporario[h][2] and i == k[1] and not estadoTemporario[h][
                            3]:  # verificando se estado de ativação é o mesmo estado resultante com o estado de ativação da função atual
                            if k[0] != estadoTemporario[h][0]:
                                estadoTemporario[h][2] = k[2]
                                entrada += 1  # uma das modificações foram feitas
                            else:
                                if ambiguidades > 0:  # verifica se o estado de ativação da função atual possui ambiguidades, tendo que escolher o caminho definido, caso haja ambiguidades, ou apenas continuar seguindo.
                                    if estadoTemporario[h][1] == k[3]:
                                        estadoTemporario[h][2] = k[2]
                                        entrada += 1
                                else:
                                    estadoTemporario[h][2] = k[2]
                                    entrada += 1
                        h += 1
                    if entrada == len(estadoTemporario):  # feita todas as modificações dos estados armazenados
                        entrou = True
    h = 0
    while h < len(
            estadoTemporario):  # loop para verificar se alguma das maquinas que foram dividas para os estados ambíguos chegou em um estado de aceitação
        for finais in parametrosEstados[2]:  # verifica se alguma delas está no estado de aceitação(estado final)
            if estadoTemporario[h][2] == finais and estadoAtual != finais:
                estadoAtual = estadoTemporario[h][2]
        h += 1

    if estadoAtual in parametrosEstados[2]:  # se estiver no estado final, palavra aceita
        return 'Palavra Aceita!!!'
    else:  # senão, é rejeitada
        return 'Palavra Rejeitada!!!'

class Simular(Screen):
    arquivo = None
    minimizado = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self, *args):
        self.manager.get_screen('simular').ids.palavra.focus = True
        try:
            self.arquivo = leituraArquivo('automato')
            self.minimizado = conversaoAFN(self.arquivo)
            criacaoArquivo(self.minimizado, 'automato minimizado')
            criarGrafo(self.arquivo, 'fotoautomato')
        except FileNotFoundError:
            self.manager.current = 'cadastro1'
        finally:
            self.manager.get_screen('simular').ids.imagem.source = diretorioImagem('fotoautomato')
            pass

    def testar(self, *args):
        self.manager.get_screen('simular').ids.mensagemautomato.text = 'Automato Original: ' + simulacao(self.arquivo, self.manager.get_screen('simular').ids.palavra.text)
        self.manager.get_screen('simular').ids.mensagemminimizado.text = 'Automato Minimizado: ' + simulacao(self.minimizado, self.manager.get_screen('simular').ids.palavra.text)
        pass

class Menu(Screen):
    pass

class MeuApp(App):
    def build(self):
        return Telas()

if __name__ == '__main__':
    MeuApp().run()
