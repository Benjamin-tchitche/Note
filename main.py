
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

from kivymd.app import MDApp

import time,os
import note_backend


Builder.load_file("templates/note.kv")


note_name = None
current_tag = None

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
    tag = StringProperty()
    parametrer = DictProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_press(self):
        
        global note_name 
        global current_tag
        note_name = self.title
        current_tag = self.tag
        
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
        self.standare = ["Note","Journal","Penser-bêtes","Tâche","Tableau de Donnés"]
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
            
            if current_tag != None:
                self.categorie = current_tag
        
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
                                        tag = current_tag,
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


class ItemConfirm(OneLineAvatarIconListItem):
    divider = None
    ischeck = BooleanProperty(False)

    def set_icon(self, instance_check):
        
        if instance_check.active:
            instance_check.active = False
            self.ischeck = False
        else: 
            instance_check.active = True
            self.ischeck = True
            
        

class NoteShow(MDScreen):
    Text = StringProperty()
    note_title = StringProperty()
    
    dataObject = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        self.dialog = None
    
    def on_parent(self, widget, parent):
        if self.login:
            self.dialog = None
            if note_name != None:
                self.exist = True
                self.dataObject = note_backend.note_databse.get(title = note_name)[0]
                self.note_title = self.dataObject.title
                if current_tag != "Tableau de Donnés":
                    self.Text = self.parsing(self.dataObject.note_text)
                else:
                    self.data = self.parsing(self.dataObject.note_text)
                    
                    self.tables = MDDataTable(
                        size_hint =(1,1),
                        use_pagination=False,
                        check = True,
                        column_data=[(k, dp(30)) for k in self.data[0]],
                        row_data = self.data[1],
                        rows_num = len(self.data[1])
                    )
                   
                    self.ids["show_Box"].clear_widgets()
                    self.ids["show_Box"].add_widget(self.tables)
                    
        
        self.login = not self.login
    
    def parsing(self,md_text) -> str:
        parsed_text = ""
        if current_tag == "notes":
            parsed_text = self.note_parsing(md_text)
        elif current_tag == "Tableau de Donnés":
            parsed_text = self.data_table_parsing(md_text)
                
        return parsed_text
    
    def data_table_parsing(self,text:str):
        header = []
        data = []
        lines = text.split("\n")
        for line in lines:
            if line.startswith("#"):
                header = line.replace("#","").split('-')
            else:
                data.append(line.split('-'))
            
        return (header, data)
    
    def note_parsing(self,text):
        lines = text.split("\n")
        
        parsed_text = ""
        for line in lines:
            line = line.strip()
            if line.startswith("# "):  # Titre de niveau 1
                line = f"[b][size=24]{line[2:]}[/size][/b]"
            elif line.startswith("## "):  # Titre de niveau 2
                line = f"[b][size=20]{line[3:]}[/size][/b]"
            elif line.startswith("### "):  # Titre de niveau 3
                line = f"[b][size=18]{line[4:]}[/size][/b]"
            elif line.startswith("- ") or line.startswith("* "):  # Liste
                line = f"[b][size=20]• [/size][/b]{line[2:]}"
            
            if "*" in line:  # Texte en gras
                line = line.replace("*", "[b]").replace("*", "[/b]", 1)
            if "_" in line:  # Texte en italique
                line = line.replace("_", "[i]").replace("_", "[/i]", 1)
            
            
            parsed_text += f"{line}\n"
    
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
    
    def setting(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Choisir les parametres",
                type="confirmation",
                items=[
                    ItemConfirm(text="case à cochée"),
                    ItemConfirm(text="notification"),
                    
                ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.cancel,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.get_settings
                    ),
                ],
            )
        self.dialog.open()
    
    def cancel(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        
    def get_settings(self,*args):
        sett = []
        for el in self.dialog.items:
            if el.ischeck:
                sett.append(el.text)
        
        # enregistrement et reload
        
        self.dialog.dismiss()
        
        
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
                    title = obj.title,
                    tag = obj.tag
                )
                
                self.ids['contener'].add_widget(note)
                
        self.login = not self.login
    
    def add_new(self):
        global note_name 
        note_name = None 
        sm.current = "OptionsScreen"
        sm.transition.direction = 'left'

class OptionTemplate(MDCard):
    Name = StringProperty()
    image = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_press(self):
        global current_tag
        
        current_tag = self.Name
        sm.current = "NoteEditScreen"
        sm.transition.direction = 'left'
        
        
        
class OptionsScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.image_path = os.path.join(note_backend.assets_path,'image')
        self.template = {
            "Journal": os.path.join(self.image_path,"journal.jpeg"),
            "Notes" : os.path.join(self.image_path,"note.jpeg"),
            "Tableau de Donnés": os.path.join(self.image_path,"datatble.png"),
            "Tâches": os.path.join(self.image_path,"task.png")
        }
        
        self.login = True
    
    def on_parent(self,widget, parent):
        
        if self.login:
            self.load()
        
        self.login = not self.login
    
    def load(self): 
        self.ids["contener"].clear_widgets()
        for tmp in self.template.keys():
            shw = OptionTemplate(
                Name = tmp,
                image = self.template.get(tmp)
            )
            
            self.ids["contener"].add_widget(shw)
            
            
        
    
    def back(self):
        global note_name
        self.exist = False 
        note_name = None
        sm.current = "NoteMainScreen"
        sm.transition.direction = 'right'

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
        sm.add_widget(
            OptionsScreen(name="OptionsScreen")
        )

        return sm
    



if not os.path.exists("databases/note_base.db"):
    os.mkdir("databases")
    note_backend.note_databse.create()
    
NoteApp().run()