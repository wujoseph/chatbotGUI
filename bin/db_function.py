from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import time
import json
from bin.temp_llm import generate_output

class learning_project_function:
    def __init__(self,db):
        self.db = db


    def db_select_test(self):
        sql_cmd = """
        select *
        from test
        """

        # sqlalchemy ver 2.0, need to use with statement, and text() function
        with self.db.engine.connect() as conn:
            query_data = conn.execute(text(sql_cmd))
            st = ""
            for i in query_data:
                #print(i)
                st += str(i)
            #print("---------select end----")
            return st
        
    def db_insert_test(self):
        sql_cmd = """
        INSERT INTO test
        VALUES(777,'newinsert');
        """
        # sqlalchemy ver 2.0, need to use with statement, and text() function
        with self.db.engine.connect() as conn:
            conn.execute(text(sql_cmd))
            conn.commit()
            #print('---------insert end----')


    def check_google_api(self,key):
        sql_cmd = """
        select *
        from user
        where apikey='""" + key + "'"

        # sqlalchemy ver 2.0, need to use with statement, and text() function
        with self.db.engine.connect() as conn:
            query_data = conn.execute(text(sql_cmd))
            for i in query_data:
                #print(i)
                return True # apikey is valid           
        return False
    
    def chat_history(self,apikey, character):
        if(apikey is None or character is None):
            return ""
        sql_cmd = """
        select *
        from chathistory
        where apikey='""" + apikey + "' AND charac='" +  character +"' ORDER BY time DESC"
        # using 'charac' column in sql table, due to reserved word

        # sqlalchemy ver 2.0, need to use with statement, and text() function
        with self.db.engine.connect() as conn:
            query_data = conn.execute(text(sql_cmd))
            for i in query_data:
                #print(i)
                #print(i[2])
                return i[2]
                # here the data is in single quote
    
    # about the data
    # notice there are different type of string in data structure
    # in mysql db, we use single quote
    # and in python, we use double quote
    # in js we we also use double quote

    def new_chat(self, apikey, chat, character):
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(now_time)
        #print(apikey, character)
        # chat_his = '"' + self.chat_history(apikey, character) + '"'
        chat_his = self.chat_history(apikey, character).replace("'", '"')
        chat_his_json = json.loads(chat_his)
        
        llm_output = generate_output(chat) # this part will take some time

        chat_his_json.append([chat, llm_output])
        chat_his = json.dumps(chat_his_json, ensure_ascii=False)

        sql_cmd = """
        insert into chathistory
        """ + f"values('{now_time}', '{apikey}', '{chat_his}', '{character}');"
        #print(sql_cmd)
        with self.db.engine.connect() as conn:
            conn.execute(text(sql_cmd))
            conn.commit()


    
    