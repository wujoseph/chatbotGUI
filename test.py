from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__,static_url_path='', 
            static_folder='')

@app.route('/Test')
def login():
    return "hello world"

if __name__ == "__main__":
    app.run(host='localhost', port=5000)