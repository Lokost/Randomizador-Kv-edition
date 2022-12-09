# coding: UTF-8
# Arquivo: adapter

# RecyclerView imports
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.label import Label

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    '''Adiciona seleção e foco para o item selecionado'''

class SelectableLabel(RecycleDataViewBehavior, Label):
    '''Adiciona suporte de seleção para a Label'''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    value = None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)
    
    def on_touch_down(self, touch):
        '''Adiciona a função "On touch down"'''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        '''Responde à seleção dos itens na view'''
        self.selected = is_selected

        if is_selected:
            self.value = rv.data[index]['text']
        else:
            self.value = None

# Fim