
from model import Model
import pathlib,os

not_fields = [
        ('id','INTEGER PRIMARY KEY'),('categorie','TEXT'),('title','TEXT'),
        ('note_text','TEXT'),('date','TEXT'),('run_date','TEXT')
            ]

settings_fields = [
        ('id','INTEGER PRIMARY KEY'),('tag','TEXT'),('categorie','TEXT'),('title','TEXT'),
        ('note_text','TEXT'),('date','TEXT'),('run_date','TEXT')
            ]

user_settings = [
        ('id','INTEGER PRIMARY KEY'),('pwd','TEXT')
            ]
note_databse = Model(not_fields, "databases/note_base.db", "notes")

user_database = Model(user_settings, "databases/note_base.db", "user_settings")
#settings_databse = Model(settings_fields, "databases/note_base.db", "settings")

base_path = pathlib.Path(__file__).parent
assets_path = os.path.join(base_path,'assets')
