
from model import Model
import pathlib,os

not_fields = [
        ('id','INTEGER PRIMARY KEY'),('tag','TEXT'),('categorie','TEXT'),('title','TEXT'),
        ('note_text','TEXT'),('date','TEXT'),('run_date','TEXT')
            ]

note_databse = Model(not_fields, "databases/note_base.db", "notes")

base_path = pathlib.Path(__file__).parent
assets_path = os.path.join(base_path,'assets')
