
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty,ObjectProperty


from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp

import time,os
import note_backend


Builder.load_file("templates/note.kv")


note_name = None

class Item(OneLineAvatarIconListItem):
    left_icon = StringProperty()
    right_icon = StringProperty()
    right_text = StringProperty()

class RightContentCls(IRightBodyTouch, MDBoxLayout):
    icon = StringProperty()
    text = StringProperty()

class NoteBox(MDCard):
    categorie = StringProperty("")
    run_date = StringProperty("Non spécifier")
    create_date = StringProperty("")
    title = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_press(self):
        
        global note_name 
        note_name = self.title
        
        sm.current = "NoteShow"
        sm.transition.direction = 'left'
        


class NoteEditScreen(MDScreen):
    categorie = StringProperty()
    run_date = StringProperty("Non spécifier")
    create_date = StringProperty("")
    title = StringProperty("")
    note_text = StringProperty()
    
    exist = BooleanProperty(False)
    dataObject = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standare = ["Défaut","Professionnelle","Penser-bêtes","Nouveautés"]
        self.icons = [""]
        self.categorie = self.standare[0]
        
        self.login = True
        
        self.datas = {}
    def on_parent(self,widget, parent):
        self.categorie = self.standare[0]
        self.create_date = ""
        self.title = ""
        self.note_text = ""
        
        if self.login:
            if note_name != None:
                self.exist = True
                self.dataObject = note_backend.note_databse.get(title = note_name)[0]
                self.categorie = self.dataObject.categorie
                self.title = self.dataObject.title
                self.note_text = self.dataObject.note_text
        
        self.login = not self.login
            
    def open_menu(self,x):
        
        menu_items = [
            {
                "text": f"{i}",
                "right_text": "+Shift+X",
                "right_icon": "apple-keyboard-command",
                "viewclass": "Item",
                "height": dp(54),
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i in self.standare
        ]
        self.menu = MDDropdownMenu(caller=x, 
            items=menu_items,md_bg_color="#bdc6b0",
            width_mult=4,)
        self.menu.open()
        
        
    def menu_callback(self, text_item):
        self.ids["drop_text"].text = text_item
        self.menu.dismiss()
    
    def save(self):
        self.datas["categorie"] = self.ids["drop_text"].text
        self.datas["title"] = self.ids["note_title"].text
        self.datas["Text"] = self.ids["note_text"].text
        
        date = time.strftime("%H:%M  %d/%m/%Y")

        if not self.exist:
            note_backend.note_databse.add(title = self.datas["title"],
                                        note_text = self.datas["Text"],
                                        categorie = self.datas["categorie"],
                                        date = date
                                        )
        else:
            self.dataObject.title = self.datas["title"]
            self.dataObject.note_text = self.datas["Text"]
            self.dataObject.categorie = self.datas["categorie"]
            self.dataObject.save()
            
        self.back()
    
    
    
    def back(self):
        global note_name
        self.exist = False 
        note_name = None
        sm.current = "NoteMainScreen"
        sm.transition.direction = 'right'

class NoteShow(MDScreen):
    Text = StringProperty()
    note_title = StringProperty()
    
    dataObject = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
    
    def on_parent(self, widget, parent):
        if self.login:
            if note_name != None:
                self.exist = True
                self.dataObject = note_backend.note_databse.get(title = note_name)[0]
                self.note_title = self.dataObject.title
                self.Text = self.dataObject.note_text
        
        self.login = not self.login
    
    def parsing(self,text) -> str:
        pass
    
    def update(self):
        global note_name 
        note_name = self.title
        
        sm.current = "NoteEditScreen"
        sm.transition.direction = 'left'
    
    def delete(self):
        self.dataObject.remove()
        self.back()
    
    def back(self):
        global note_name
        self.exist = False 
        note_name = None
        sm.current = "NoteMainScreen"
        sm.transition.direction = 'right'
        
class NoteMainScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        

    def on_parent(self, widget, parent):
        if self.login:
            datas = note_backend.note_databse.all(reverse = True , order_col = 'date')
            self.ids['contener'].clear_widgets()
            for obj in datas:
                note = NoteBox(
                    categorie = obj.categorie,
                    create_date = obj.date,
                    title = obj.title
                )
                
                self.ids['contener'].add_widget(note)
                
        self.login = not self.login
    
    def add_new(self):
        global note_name 
        note_name = None 
        sm.current = "NoteEditScreen"
        sm.transition.direction = 'left'
        
class NoteApp(MDApp):
    def build(self):
        global sm
        sm = MDScreenManager()
        
        sm.add_widget(
            NoteMainScreen(name="NoteMainScreen")
        )
        sm.add_widget(
            NoteShow(name="NoteShow")
        )
        sm.add_widget(
            NoteEditScreen(name="NoteEditScreen")
        )

        return sm
    



if not os.path.exists("databases/note_base.db"):
    os.mkdir("databases")
    note_backend.note_databse.create()
    
NoteApp().run()