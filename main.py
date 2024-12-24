
from kivy.config import Config
Config.set('kivy', 'window_icon', 'assets/image/note.png')

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty,ObjectProperty,DictProperty
from kivy.utils import get_hex_from_color

from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors.focus_behavior import FocusBehavior
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.button import MDFlatButton, MDTextButton
from kivymd.uix.dialog import  MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers.colorpicker import MDColorPicker



from kivymd.app import MDApp
from typing import Union

import time,os
import note_backend


Builder.load_file("templates/note.kv")


# global variable
note_name = None
settings_tag = None 


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
    
    def settings(self):
        sm.current = "Settings"
        sm.transition.direction = 'left'
    
    def add_new(self):
        global note_name 
        note_name = None 
        sm.current = "NoteEditScreen"
        sm.transition.direction = 'left'


class ItemConfirm(OneLineAvatarIconListItem):
    divider = None
   
    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class Settings(MDScreen):
    text_font = StringProperty()
    title_font = StringProperty()
    subtitle_font = StringProperty()
    subsubtitle_font = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = False
    
    def on_parent(self, widget, parent):
        if not self.login: 
            self.text_font = note_backend.settings_databse.get(tag = 'text')[0].font.split('/')[-1].split('.')[0]
            self.title_font = note_backend.settings_databse.get(tag = 'title')[0].font.split('/')[-1].split('.')[0]
            self.subtitle_font = note_backend.settings_databse.get(tag = 'subtitle')[0].font.split('/')[-1].split('.')[0]
            self.subsubtitle_font = note_backend.settings_databse.get(tag = 'subsubtitle')[0].font.split('/')[-1].split('.')[0]
            
            self.ids["theme_mode"].active = True if note_backend.user_database.get(id = 1)[0].theme == "Dark" else False
    
    def theme_update(self,x):
        obj = note_backend.user_database.get(id = 1)[0]
        
        obj.theme = "Dark" if x.active else "Light"
        self.theme_cls = obj.theme
        
        obj.save()
        
    def update_font(self, tag):
        global settings_tag 
        settings_tag = tag 
        sm.current = "FontsSettingsScreen"
        sm.transition.direction = 'left'
        
    def back(self):
        sm.current = "NoteMainScreen"
        sm.transition.direction = 'right' 
 
class FontBox(MDCard):
    press_fonc = ObjectProperty()
    font_name = StringProperty()
    
    def  __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_press(self):
        self.press_fonc(self.font_name)
        
class FontsSettingsScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = {
            'tag':'title',
            'font':'assets/fonts/PlaywriteCOGuides-Regular.ttf',
            'font_size':16,
            'bold':0,
            'italic': 0,
            'underline': 0,
            'color': '#fffff'
            
        }
        self.login = False
        self.fonts = note_backend.get_fonts()
    
    def on_parent(self, widget, parent):
        if not self.login:
            self.settings['tag'] = settings_tag
            obj = note_backend.settings_databse.get(tag = settings_tag)[0]
            self.settings['font'] = obj.font
            self.settings['font_size'] = obj.font_size
            self.settings['bold'] = obj.bold
            self.settings['italic'] = obj.italic
            self.settings['underline'] = obj.underline
            self.settings['color'] = obj.color
            box_contener = self.ids["box_contener"]
            box_contener.clear_widgets()
            
            for font in self.fonts:
                box_contener.add_widget(
                    FontBox(font_name = font,press_fonc = lambda x : self.font_update(x))
                )
        
        
        self.login = not self.login
    
    def bold_update(self):
        if self.settings.get('bold') == 1:
            self.settings['bold'] = 0
        else:
            self.settings['bold'] = 1
        
        self.update_overview()
    
    def italic_update(self):
        if self.settings.get('italic') == 1:
            self.settings['italic'] = 0
        else:
            self.settings['italic'] = 1
        
        self.update_overview()

    
    def underline_update(self):
        if self.settings.get('underline') == 1:
            self.settings['underline'] = 0
        else:
            self.settings['underline'] = 1
        
        self.update_overview()
    
    def font_update(self,font):
        self.settings['font'] = f"assets/fonts/{font}"
        
        self.update_overview()
    
    def font_size_update(self,size):
        self.settings['font_size'] = size
        
        self.update_overview()
    
    def color_update(self, color: list):
        self.settings['color'] = get_hex_from_color(color)
        self.update_overview()
    
    def update_overview(self):
        #l = MDLabel()
        lab = self.ids["overview"]
        lab.font_name = self.settings['font']
        lab.font_size = self.settings['font_size']
        lab.bold = bool(self.settings['bold'])
        lab.italic = bool(self.settings['italic'])
        lab.underline = bool(self.settings['underline'])
        lab.color = self.settings['color']
        
    
    def open_color_picker(self):
        self.color_picker = MDColorPicker(size_hint=(0.45, 0.85), type_color="HEX")
        self.color_picker.open()
        self.color_picker.bind(
            #on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
        )
        
    def get_selected_color(
        self,
        instance_color_picker: MDColorPicker,
        type_color: str,
        selected_color: Union[list, str],
    ):
        '''Return selected color.'''
        self.color_update(selected_color[:-1] + [1])
        self.color_picker.dismiss()
    
    def save(self):
        obj = note_backend.settings_databse.get(tag = self.settings['tag'])[0]
        obj.font=self.settings['font']
        obj.font_size =self.settings['font_size']
        obj.bold =self.settings['bold']
        obj.italic = self.settings['italic']
        obj.underline = self.settings['underline']
        obj.color =self.settings['color']
        obj.save()
        self.back()
    
    def back(self):
        sm.current = "Settings"
        sm.transition.direction = 'right'
    
class NoteApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = note_backend.user_database.get(id=1)[0].theme
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
        sm.add_widget(
            Settings(name="Settings")
        )
        sm.add_widget(
            FontsSettingsScreen(name="FontsSettingsScreen")
        )

        return sm
    
if not os.path.exists("databases/note_base.db"):
    os.mkdir("databases")
    note_backend.note_databse.create()
    note_backend.settings_databse.create()
    note_backend.user_database.create()
    
    note_backend.user_database.add(theme = "Dark")
    
    note_backend.settings_databse.add(tag = 'title', 
        font="assets/fonts/RobotoMono-Thin.ttf",
        font_size = 24,
        bold = 1,
        italic = 0,
        underline = 0,
        color = 'white'
                                        )
    note_backend.settings_databse.add(tag = 'subtitle', 
        font='assets/fonts/RobotoMono-Italic.ttf',
        font_size = 20,
        bold = 1,
        italic = 0,
        underline = 0,
        color = 'white')

    note_backend.settings_databse.add(tag = 'subsubtitle',
        font="assets/fonts/RobotoMono-Regular.ttf",
        font_size = 18,
        bold = 0,
        italic = 0,
        underline = 1,
        color = 'white')
    note_backend.settings_databse.add(tag = 'text',
        font='assets/fonts/RobotoMono-Thin.ttf',
        font_size = 16,
        bold = 0,
        italic = 0,
        underline = 0,
        color = 'white')


NoteApp().run()
