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
from os.path import exists

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
    online = False

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
            if idx >= 0:
                select = lista.data[idx]['text']
                if func.gerar_lista(select):
                    data.lista = str(select)
                    data.preparada = True
                    data.historico = None
                    data.iniciada = False
                    data.quant = len(func.dados)
                    data.online = False
                    print(
                        '-'*20,
                        f'\nlista: {data.lista}',
                        f'\nPreparada: {"Sim" if data.preparada else "Não"}',
                        f'\nIniciada: {"Sim" if data.iniciada else "Não"}',
                        f'\nTamanho: {data.quant}'
                        f'\nOnline: {"Sim" if data.online else "Não"}'
                    )
                    self.manager.current = 'inicio'
                    self.manager.transition.direction = 'right'
                    Alerta(f'Lista aberta: {data.lista}').open()
                else:
                    raise ListError('Não foi possível abrir a lista!', select)
        
        except IndexError:
            raise ListError('Não foi possível encontrar essa lista!', '')

        except Exception as e:
            Alerta('Não foi possível abrir a lista!').open()
            print(str(e))

class Input(Popup):
    def __init__(self, mensagem: str, hint: str, **kwargs):
        self.msg = mensagem
        self.hint = hint
        super(Input, self).__init__(**kwargs)

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
    lista = str(data.lista)
    nova = False

    def on_enter(self):
        self.ids.itens.disabled = True if data.online else False
        self.lista = str(data.lista)

        self.msg = self.ids.msg
        self.search = self.ids.search
        self.obj_itens = self.ids.itens
        self.add = self.ids.add
        self.rem = self.ids.rem

        if data.lista and not data.online:
            self.msg.opacity = 0
            self.search.disabled = False
            self.itens = list(func.dados) if func.gerar_lista(data.lista) else []
            self.itens_dict = func.list_to_dict(self.itens)
            self.obj_itens.disabled = False
            self.obj_itens.data = self.itens_dict
            self.add.disabled = False
            self.rem.disabled = False
        
        elif data.online:
            self.msg.opacity = 1
            self.msg.text = 'Uma lista online está aberta!'
            self.obj_itens.data = []
            self.search.disabled = True
            self.add.disabled = True
            self.rem.disabled = True
        
        elif not data.lista and not data.online:
            self.msg.opacity = 1
            self.msg.text = 'Não há uma lista aberta!'
            self.obj_itens.data = []
            self.search.disabled = True
            self.add.disabled = True
            self.rem.disabled = True
    
    def pesquisa(self):
        pesquisa = self.ids.search.text
        if not pesquisa:
            self.itens_dict = func.list_to_dict(self.itens)
            self.obj_itens.data = self.itens_dict
        else: 
            self.itens_dict = func.list_to_dict([x for x in self.itens if pesquisa.lower() in x.lower()])
            self.obj_itens.data = self.itens_dict

    def salvar(self):
        def retorno(*args):
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'right'

        if data.lista or self.nova:
            func.salvar_arquivo(self.lista, self.itens)
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
                self.obj_itens.data = self.itens_dict
                data.item = ''
        
        if data.lista or self.nova:
            popup = Input('Digite o item a ser adicionado:', 'Item')
            popup.bind(on_dismiss=add)
            popup.open()

    def n_lista(self):
        def nome_lista(*args):
            if data.item:
                self.lista = data.item if '.txt' in data.item[-4:] else data.item + '.txt'
                data.item = None

                if exists(f'listas/{self.lista}'):
                    Alerta('Já existe uma lista com esse nome!').open()
                    return None

                self.obj_itens.data = []
                self.add.disabled = False
                self.rem.disabled = False
                self.obj_itens.disabled = False
                self.search.disabled = False
                self.msg.opacity = 0
                self.nova = True

                self.itens.clear()
                self.itens_dict.clear()

                Alerta('Lista criada! *Se sair do editor, ela será apagada!')

        popup = Input('Digite o nome da nova lista:', 'Nova lista')
        popup.bind(on_dismiss=nome_lista)
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

class AddOnline(Popup):
    def adicionar(self):
        apelido = self.ids.apelido.text
        url = self.ids.url.text

        if not apelido or not url:
            Alerta('Não é possível adicionar! Falta algo!').open()
            self.ids.apelido.focus = True
        
        else:
            if func.add_online({
                'apelido': apelido,
                'url': url
            }):
                alerta = Alerta('Adicionada com sucesso!')
                alerta.bind(on_dismiss=self.dismiss)
                alerta.open()
                
            else:
                Alerta('Algo deu errado, verifique o que foi inserido!').open()
                self.ids.apelido.focus = True

class Online(Screen):
    def get_data(self, *kwargs):
        self.ids.listas.data = func.list_to_dict(func.get_online_lists())

    def add_online(self):
        add = AddOnline()
        add.bind(on_dismiss=self.get_data)
        add.open()

    def get_online(self):
        lista = self.ids.listas
        idx = lista.layout_manager.selected_nodes[0]

        try:
            if idx >= 0:
                select = lista.data[idx]['text']
                if func.gerar_lista(select, True):
                    data.lista = str(select)
                    data.preparada = True
                    data.historico = None
                    data.iniciada = False
                    data.quant = len(func.dados)
                    data.online = True
                    print(
                        '-'*20,
                        f'\nlista: {data.lista}',
                        f'\nPreparada: {"Sim" if data.preparada else "Não"}',
                        f'\nIniciada: {"Sim" if data.iniciada else "Não"}',
                        f'\nTamanho: {data.quant}'
                        f'\nOnline: {"Sim" if data.online else "Não"}'
                    )
                    self.manager.current = 'inicio'
                    self.manager.transition.direction = 'right'
                    Alerta(f'Lista aberta: {data.lista}').open()
                
                else:
                    raise ListError('Não possível abrir a lista online!', select)
        
        except ListError:
            Alerta('Não foi possível abrir a lista online!').open()
        

class WindowManager(ScreenManager): pass

builder = Builder.load_file(resourcePath('./randomizador.kv'))

class MainApp(App):
    title = "Randomizador"
    def build(self):
        return builder

if __name__ == '__main__':
    MainApp().run()

# Fim