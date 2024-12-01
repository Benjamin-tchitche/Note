
import sqlite3

 
class Model:
    """
    Field representation:
        fields = [
                ('id','INTEGER PRIMARY KEY'),('nom','TEXT','UNIQUE'),('prenom','TEXT','UNIQUE'),
                ('age','INTEGER','NOT NULL')
            ]
    """

    def __init__(self, fields=None, base_name='sql.db', name='tables'):
        if fields is None:
            fields = []
        self.fields = fields
        self.base_name = base_name
        self.name = name

    def __executereq(self, req, param=()):
        self.connexion = sqlite3.connect(self.base_name)
        self.cursor = self.connexion.cursor()
        try:
            self.cursor.execute(req, param)
            if ('SELECT' in req.upper()) or ('PRAGMA' in req.upper()):

                res = self.cursor.fetchall()
                return res
        except Exception as e:
            self.connexion.rollback()
            print(req, param)
            print(type(e), e)

        finally:
            self.connexion.commit()
            self.connexion.close()

    def executerSQL(self, req, param):
        return self.__executereq(req, param)
    
    def create(self) -> None:
        """
        CREATE TABLE {nom_de_la_table}(nom_champ1 typechamp1, ...,)
        """
        if self.fields[0][0] != 'id' and self.fields[0][1] != 'INTEGER PRIMARY KEY':
            self.fields.insert(0, ('id', 'INTEGER PRIMARY KEY'))

        columns = ''

        req = "CREATE TABLE IF NOT EXISTS '{0}'(".format(self.name)
        for champ in self.fields:
            if champ[0] != 'id':
                columns += " '{0} ' ".format(str(champ[0]))
            for col in champ:
                if col == champ[0]:
                    req += f"'{col}' "
                else:
                    req += col + ' '

            req += ", "
        req = req[:-2] + ")"
        self.__executereq(req=req)

    def add(self, data=None, **kwargs) -> None:
        if data is not None and isinstance(data, dict):
            kwargs = data

        req = f"INSERT INTO '{self.name}' ("
        param = []

        for key in kwargs:
            req += f"'{key}' ,"
            param.append(kwargs[key])

        req = req[:-1] + ') VALUES ('
        for i in range(len(param)):
            req += '? , '
        req = req[:-2] + ')'
        self.__executereq(req, tuple(param))

    def add_many(self,data=None):
        """add_many
        Args:
            data : list[list] | liste des donnés sans les colones
        """
        req = f"INSERT INTO '{self.name}' ("
        for tp in self.fields:
            if (tp[0]) != 'id':
                req += f"'{tp[0]}' ,"
        
        req = req[:-1] + ') VALUES ('
        for i in range(len(data[0])):
            req += '? , '
        req = req[:-2] + ')'
        
        try:
            self.connexion = sqlite3.connect(self.base_name)
            self.cursor = self.connexion.cursor()
            self.cursor.executemany(req, data)
        except Exception as e:
            self.connexion.rollback()
            
        finally:
            self.connexion.commit()
            self.connexion.close()

    
    def add_fields(self, fields=None) -> None:
        """
        ajoute une ou plusieurs champs dans la table
        :param fields: les champ à ajouter
                fields = [(nom_champ,type_champ,...), ...]
        """
        if fields is not None:
            for field in fields:
                req = f"ALTER TABLE '{self.name}' ADD "
                req += f"'{field[0]}' {field[1]}"
                self.__executereq(req)

    def remove_fields(self, fields=None) -> None:
        """
        supprime une ou plusieurs champs de la table
        :param fields: les champ à supprimer
                fields = [(nom_champ,), ...]
        """
        if fields is not None:
            for field in fields:
                req = f"ALTER TABLE '{self.name}' DROP COLUMN "
                req +=f"'{field[0]}'"
                self.__executereq(req)

    def rename_field(self, field_name, new_name):
        req = f"ALTER TABLE '{self.name}' RENAME column '{field_name}' TO '{new_name}'"
        self.__executereq(req)

    def rename_table(self, table, new_name) -> None:
        """
        renomer une table
        :param table: str [le nome de la table à renomer]
        :param new_name: str [nouveau nom à donner à la table]
        :return: None
        """
        req = f"ALTER TABLE '{table}' RENAME TO '{new_name}'"
        self.__executereq(req)

    def get_tables_meta(self, table=None) -> list:
        """
        cette methode renvoie la liste des colonnes d'une table
        :param table: str
        :return: list
        """
        if table is None:
            table = self.name
        req = f"PRAGMA table_info('{table}')"
        meta = self.__executereq(req)

        ls = []
        if meta:
            for champ in meta:
                ls.append(champ[1])

        return ls

    def get_tables(self) -> list[tuple]:
        req = "SELECT name FROM sqlite_master WHERE TYPE='table'"
        return self.__executereq(req)

    def all(self, reverse = False, order_col = 'id') -> list:
        req = f"SELECT* FROM '{self.name}' "
        if reverse:
            req += f" ORDER BY {order_col} DESC"
        else:
            req += f" ORDER BY {order_col}"
            
        values = self.__executereq(req)
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )
            
        return data

    def get(self, reverse = False, order_col = 'id', data=None, **kwargs) -> list:
        """
        cette methode permet de recuperer un element de la base de donnée
        :param data: dict
        :return: list[tuple]
        """
        if data is not None and isinstance(data, dict):
            kwargs = data

        req = f"SELECT* FROM '{self.name}' WHERE "
        param = []
        for key in kwargs:
            for tp in self.fields:
                if tp[0] == key:
                    req += key + ' = ? AND '
                    param.append(kwargs[key])
        
        req = req[:-4]
        if reverse:
            req += f" ORDER BY {order_col} DESC"
        else:
            req += f" ORDER BY {order_col}"
        
        
        values = self.__executereq(req, tuple(param))
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )
        return data
    
    def get_by_column(self, cols:str):
        req = f"SELECT {cols} FROM '{self.name}'"

        values = self.__executereq(req)
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )

        return data
    
    
    def update(self,col, value,setcond) -> None:
        """col       : str          | colone à modiffier
            value    : str          | nouvelle valeur 
            setcond  : expression   | condition d'arrêt
                                    | exemple: <colone> '<=' valeur 
                                    | important si on veux pas modiffier toutes les lignes
        """
        req=f'UPDATE "{self.name}" SET "{col}" = "{value}" '
        if setcond is not None:
            req += f' WHERE {setcond}'

     
        self.__executereq(req)

    def delete_all(self) -> None:
        """cette methode supprime tous les donnés de la table"""

        req = f"DELETE FROM '{self.name}'"
        self.__executereq(req)
    
    def delete_table(self, table_name) -> None:
        """ cette methode supprime la table de la base de données
        """
        req = f"DROP TABLE '{table_name}' "
        self.__executereq(req)

    def remove(self, data=None, **kwargs) -> None:
        """cette methode supprime un ou plusieurs elements de la table
        data : dict
        """
        if data is not None and isinstance(data, dict):
            kwargs = data
        req = f"DELETE FROM '{self.name}' WHERE "
        param = []
        for key in kwargs:
            req += f"{key}=? AND"
            param.append(kwargs[key])

        req = req[:-3]
        self.__executereq(req, param=tuple(param))


class DataObject:
    def __init__(self, fields, datas, base_name, table_name) -> None:
        self.fields = fields
        self.base_name = base_name
        self.name = table_name
        self.datas = datas
        self.data_dic = {}
        
        self.__update_content_values()
        
        self.base = Model(fields=self.fields, base_name=self.base_name,
                          name=self.name)
        
    def __update_content_values(self):
        i=0
        for field in self.fields:
            try:
                self.data_dic.update({field[0]: self.datas[i]})
            except:
                self.data_dic.update({field[0]: None})
            i += 1
        self.__dict__.update(self.data_dic)
        
    def __str__(self) -> str:
        self.__unp()
        return f"{self.data_dic}"
    
    def __unp(self):
        for key in self.data_dic.keys():
            self.data_dic[key]= self.__dict__[key]
    
    
    def save(self):
        if self.isExist():
            for key in self.__dict__.keys():
                if key != 'id' and key in self.data_dic.keys():
                    self.base.update(col=key, value=self.__dict__[key], 
                                    setcond=f'id={self.__dict__["id"]}')
        else:
            self.base.add(data=self.data_dic)
            
            
    def remove(self):
        self.base.remove(id=self.__dict__["id"])
    
    def newTableToConnect(self, name):
        self.base = Model(base_name=self.base_name,
                          name=name)
        self.fields = [(fd,) for fd in self.base.get_tables_meta(name)]
        self.base.fields = self.fields
        
        self.__update_content_values()
    
    def isExist(self) -> bool:
        values = self.base.get(id=self.__dict__["id"])
        if values is None or len(values) == 0:
            return False
        
        return True

if __name__ == '__main__':
    fields = [('id', 'INTEGER PRIMARY KEY'), ('nom', 'TEXT', 'UNIQUE'), ('prenom', 'TEXT', 'UNIQUE'),
              ('age', 'INTEGER', 'NOT NULL')
              ]
    model = Model(fields=fields, name='aa_tb',base_name='test.sqlite3')
   
    #model.create()
    data = model.all()[0]
    data.nom = "BALA"
    
    data.save()
    print(data)
