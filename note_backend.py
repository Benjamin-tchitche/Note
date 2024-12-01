
from model import Model


not_fields = [
        ('id','INTEGER PRIMARY KEY'),('categorie','TEXT'),('title','TEXT'),
        ('note_text','TEXT'),('date','TEXT'),('run_date','TEXT')
            ]

note_databse = Model(not_fields, "databases/note_base.db", "notes")
