# coding: UTF-8
# Arquivo: Func

from json import dump, loads
from os import listdir, remove, mkdir
from random import choice, randint
from fnmatch import filter
from os.path import join, abspath, dirname
import sys
import codecs

class Func:
    # Listas
    dados = list()
    completa = list()
    recentes = list()

    # Escolhas
    escolha = str()
    aux = str()

    # Info da classe
    iniciado = bool()
    opcoes = dict()

    def __init__(self) -> None:
        self.obter_listas()

    @staticmethod
    def obter_listas() -> list:
        '''Obtaining lists method'''
        try:
            a = filter(listdir('listas'), '*.txt')
            return a
        except FileNotFoundError:
            mkdir('listas')
            return []

    def gerar_lista(self, lista: str, online: bool = False) -> list | bool:
        '''Convets the file or text for lists
        lista: path of the text where contains the list.
        online: True - Transforms a loaded online list, False - Transforms the local file choosed'''

        if not online:
            # If not is online, it will open normaly the file of the path.
            try:
                with open(f'listas/{lista}', encoding='utf-8') as arq:
                    dados = arq.read().split('\n')
                    self.dados = list(dados)
                    self.completa = list(dados)
                    self.recentes.clear()
                    print(f'Lista aberta: {lista}')
                    return self.dados
            
            except FileNotFoundError:
                return False

        else:
            print('Function not applied')
            pass

    def random_choice(
        self, 
        num: bool = False,
        minimum: int = 0,
        maximum: int = 0,
        quanti: int = 1,
        repeat: bool = False
    ) -> list | str:

        def resume() -> list:
            if self.iniciado:
                self.recentes.append(self.aux)
                r_recentes = list(self.recentes)
                r_recentes.reverse()
                self.aux = self.escolha 
                print(f'{"-"*12}\nRepete: {"Sim" if repeat else "Não"}\nItem escolhido: {self.escolha}')
                resultado = [self.escolha, '\n'.join(r_recentes), len(self.dados) if not repeat else "Infinitos"]
                return resultado

            else:
                self.iniciado = True
                self.aux = self.escolha
                resultado = [self.escolha, '', len(self.dados) if not repeat else "Infinitos"]
                print(f'{"-"*12}\nRepete: {"Sim" if repeat else "Não"}\nItem escolhido: {self.escolha}')
                return resultado

        if repeat and not num and self.completa:
            self.escolha = choice(self.completa)
            while self.escolha == self.aux:
                self.escolha = choice(self.completa)
                print(self.completa, self.escolha)

        elif not repeat and not num and self.dados:
            if len(self.dados) > 0:
                self.escolha = choice(self.dados)
                self.dados.remove(self.escolha)

        elif num:
            self.escolha = self.gerarNumeral(minimum, maximum, quanti, repeat)

        else:
            self.escolha = ''

        return resume()

    def resetar(self) -> None:
        self.recentes.clear()
        self.aux = ''
        self.escolha = ''
        self.iniciado = False

    def obterOpcoes(self) -> None:
        try:
            with open('opcoes.config',encoding='utf-8') as arq:
                self.opcoes = loads(arq.read())
        
        except FileNotFoundError:
            with open('opcoes.config', 'w', encoding='utf-8') as arq:
                self.opcoes = {
                    "som": "",
                    "vol": 1
                }
                dump(self.opcoes, arq, indent = 4, separators = (',', ':'))
       

    @staticmethod
    def salvar_arquivo(arquivo: str, lista: list) -> None:
        try:
            with codecs.open(f'listas/{arquivo}', 'w', 'utf-8') as arq:
                itens = '\n'.join(lista)
                print(itens)
                arq.write(itens)

        except (FileExistsError, FileNotFoundError, ValueError):
            print('Não foi possível salvar o arquivo')

    @staticmethod
    def list_to_dict(lista: list) -> list[dict]:
        return [{'text': str(x)} for x in lista]

    def save_options(self, som: str) -> bool:
        try:
            self.opcoes['som'] = som
            with open('opcoes.config', 'w', encoding='utf-8') as arq:
                dump(self.opcoes, arq, indent=4, separators=(',', ':'))
            return True
        except Exception as e:
            print(str(e))
            return False

def resourcePath(relativo) -> str:
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relativo)

# Fim