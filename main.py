
from kivy.config import Config
Config.set('kivy', 'window_icon', 'assets/image/note.png')

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty,ObjectProperty,DictProperty


from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors.focus_behavior import FocusBehavior
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView

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

class NoteBox(MDCard,CommonElevationBehavior,FocusBehavior):
    categorie = StringProperty("")
    run_date = StringProperty("Non spécifier")
    create_date = StringProperty("")
    title = StringProperty("")
    parametrer = DictProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True


        
    def on_press(self):
       self.validate()
            
    def validate(self):
        global note_name 
        note_name = self.title
        sm.current = "NoteShow"
        sm.transition.direction = 'left'
    
   
    def notify(self,dt):
        if not str(self.run_date).isalpha():
            pass
            
        


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
        self.standare = ["Défaut","Personnelle","Penser-bêtes","Tâche","Profesinnelle"]
        self.icons = [""]
        self.categorie = self.standare[0]
        self.parametrer = {}
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
        
        else:
            self.ids["note_title"].text = ""
            self.ids['note_text'].text = ""
            
        self.login = not self.login
            
    def open_menu(self,x):
        
        menu_items = [
            {
                "text": f"{i}",
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
        if self.exist:
            self.exist = False 
            sm.current = "NoteShow"
            sm.transition.direction = 'right'
        else:
            sm.current = "NoteMainScreen"
            sm.transition.direction = 'right'
     

class NoteShow(MDScreen):
    Text = StringProperty()
    note_title = StringProperty()
    
    dataObject = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        self.dialog = None
    
    def on_parent(self, widget, parent):
        global note_name
        
        if self.login:
            self.dialog = None
            if note_name != None:
                self.exist = True
                self.dataObject = note_backend.note_databse.get(title = note_name)[0]
                self.note_title = self.dataObject.title
                self.Text = self.parsing(self.dataObject.note_text)
                
        
        self.login = not self.login
    
    def parsing(self,md_text) -> str:
        parsed_text = ""
        parsed_text = self.note_parsing(md_text)
        
      
        return parsed_text
    
    
    def note_parsing(self,text):
        self.gon = False
        parsed_text = ""
        lines = text.split("\n")
        i=0
        for line in lines:
            line = line.strip()
            if line.startswith("# "):  # Titre de niveau 1
                line = f"[b][size=34]{line[2:].title()}[/size][/b]"
                
            elif line.startswith("## "):  # Titre de niveau 2
                line = f"[b][size=28]{line[3:].title()}[/size][/b]"
                
            elif line.startswith("### "):  # Titre de niveau 3
                line = f"[b][size=24]{line[4:].title()}[/size][/b]"
                
            elif line.startswith("- ") or line.startswith("* "):  # Liste
                line = f"{' '*4}[b][size=28]• [/size][/b]{line[2:]}"
                
            if "**" in line:  # Texte en gras
                line = line.replace("**", "[b]",1).replace("**", "[/b]",1)
                i +=1
        
                
            if "__" in line:  # Texte en italique
                line = line.replace("__", "[i]",1).replace("__", "[/i]",1)
                i += 1
        
        
            parsed_text += f"{line}\n"
       
        if i > 0:
            parsed_text = self.note_parsing(parsed_text)
            

        return parsed_text
    
    def update(self):
        global note_name 
        note_name = self.note_title
        
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

class Settings(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def back(self):
        pass 
    
class NoteApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
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
    note_backend.user_database.create()

NoteApp().run()
