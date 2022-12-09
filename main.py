# coding: UTF-8
# Arquivo: main

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ListProperty
from adapter import *
from func import *
from time import sleep
from kivy.core import window
from tkinter import filedialog
from pygame import mixer

# Classes auxiliáres

func = Func()
func.obterOpcoes()

class Player:
    def __init__(self):
        mixer.init()
        self.som = mixer.Sound(resourcePath('./bip.mp3') if not func.opcoes['som'] else func.opcoes['som'])
    
    def play(self):
        self.som.stop()
        self.som.set_volume(1 if not func.opcoes['vol'] else func.opcoes['vol'])
        self.som.play()
    
    def set_file(self, file):
        self.som = mixer.Sound(file)

player = Player()

class Data:
    preparada = bool()
    iniciada = bool()
    historico = str()
    quant = int()
    lista = str()
    repeat = False
    alterada = False

    # Variáveis temporárias
    item = str()

data = Data()

class Inicio(Screen):
    def on_enter(self): 
        if data.preparada and not data.iniciada:
            self.ids.Random.disabled = False
            self.ids.resultado.text = 'Lista pronta!'
            self.ids.restantes.text = f'Itens restantes: {data.quant}'

        if data.alterada:
            self.ids.resultado.text = 'Lista alterada!'
            data.quant = len(func.dados)
            self.ids.restantes.text = f'Itens restantes: {data.quant}'
            data.alterada = False
        

    def random(self):
        player.play()
        if func.dados and not data.repeat:
            data.iniciada = True
            escolha, data.historico, data.quant = func.random_choice(repeat = data.repeat)
            self.ids.resultado.text = escolha
            self.ids.restantes.text = f'Itens restantes: {data.quant}'

        elif data.repeat and func.completa:
            data.iniciada = True
            escolha, data.historico, _ = func.random_choice(repeat = data.repeat)
            self.ids.resultado.text = escolha
        else:
            self.ids.resultado.text = 'Lista vazia!'
            self.ids.Random.disabled = True
            preparada = False

    def repeat(self):
        data.repeat = True if self.ids.repeat.state == 'down' else False
        if data.preparada:
            if data.repeat:
                self.ids.resultado.text = 'Modo infinito!'
                self.ids.restantes.text = 'Itens restantes: Infinitos!'
                self.ids.Random.disabled = False

            elif not data.repeat and func.dados :
                self.ids.resultado.text = 'Modo finito!'
                self.ids.restantes.text = f'Itens restantes: {data.quant}'
                self.ids.Random.disabled = False

            else:
                self.ids.resultado.text = 'Lista vazia!'
                self.ids.Random.disabled = True
                preparada = False
        
        else:
            self.ids.Random.disabled = True

class History(Screen):
    def on_enter(self):
        if data.historico:
            self.ids.history.text = data.historico

class Import(Screen):
    DataList = ListProperty()
    def on_enter(self):
        self.ids.listas.data = func.list_to_dict(func.obter_listas())

    def get_data(self):
        lista = self.ids.listas
        idx = lista.layout_manager.selected_nodes[0]

        try:
            select = lista.data[idx]['text']
            func.gerar_lista(select)
            data.lista = str(select)
            print(data.lista)
            data.preparada = True
            data.historico = None
            data.iniciada = False
            data.quant = len(func.dados)
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'right'
            Alerta(f'Lista carregada {data.lista}').open()

        except Exception as e:
            print(str(e))

class AddItem(Popup):
    def adicionar(self):
        data.item = self.ids.item.text
        self.dismiss()

class Alerta(Popup):
    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        super(Alerta, self).__init__(**kwargs)

class Editor(Screen):
    itens = list()
    itens_dict = list()

    def on_enter(self):
        if data.lista:
            self.ids.msg.opacity = 0
            self.ids.search.disabled = False
            self.itens = func.gerar_lista(data.lista)
            self.itens_dict = func.list_to_dict(self.itens)
            self.ids.itens.data = self.itens_dict
    
    def pesquisa(self):
        pesquisa = self.ids.search.text
        if not pesquisa:
            self.itens_dict = func.list_to_dict(self.itens)
            self.ids.itens.data = self.itens_dict
        else:
            self.itens_dict = func.list_to_dict([x for x in self.itens if pesquisa.lower() in x.lower()])
            self.ids.itens.data = self.itens_dict

    def salvar(self):
        def retorno(*args):
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'right'

        if data.lista:
            func.salvar_arquivo(data.lista, self.itens)
            func.dados = list(self.itens)
            func.completa = list(self.itens)
            alerta = Alerta('Lista salva com sucesso!')
            alerta.bind(on_dismiss=retorno)
            alerta.open()

    def deletar(self):
        try:
            idx = self.ids.itens.layout_manager.selected_nodes[0]
            item = self.itens_dict[idx]
            self.itens.remove(item['text'])
            self.itens_dict.remove(item)
            self.ids.itens.data = self.itens_dict
        except (IndexError, ValueError):
            Alerta('Selecione um item!').open()

    def adicionar(self):
        def add(*args):
            if data.item:
                print(data.item)
                self.itens.append(data.item)
                if self.ids.search.text.lower() in data.item.lower():
                    self.itens_dict.append({'text': data.item})
                self.ids.itens.data = self.itens_dict
                data.item = ''
        
        if data.lista:
            popup = AddItem()
            popup.bind(on_dismiss=add)
            popup.open()

class Options(Screen):
    def on_enter(self, *args):
        self.ids.som.text = func.opcoes['som']
        self.path = '/'.join(func.opcoes['som'].split('/')[:-1])
        return super(Options, self).on_enter(*args)

    def open_file(self):
        caminho = filedialog.askopenfile(
            initialdir='./' if not func.opcoes['som'] else self.path,
            filetypes=(('Arquivos de som', '*.mp3 *.wav *.ogg'),)
        )

        if caminho:
            self.ids.som.text = caminho.name
    
    def save(self):
        if func.save_options(self.ids.som.text):
            Alerta('Opções salvas com sucesso').open()
            self.manager.transition.direction = 'right'
            self.manager.transition.duration = .5
            self.manager.current = 'inicio'
            player.set_file(func.opcoes['som'])
        
        else:
            Alerta('Erro ao salvar as opções.').open()

class WindowManager(ScreenManager): pass

builder = Builder.load_file(resourcePath('./randomizador.kv'))

class MainApp(App):
    title = "Randomizador"
    def build(self):
        return builder

if __name__ == '__main__':
    MainApp().run()

# Fim