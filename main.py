from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import render_template
from bin.db_function import learning_project_function
import os.path

app = Flask(__name__,template_folder='template',static_url_path='', 
            static_folder='template/css')

path = os.path.join(os.path.dirname(__file__) ,'../password.txt')
path = os.path.abspath(path)
print(path)
with open(path,'r') as f:
	mysql_account = next(f).replace('\n','')
	mysql_password = next(f).replace('\n','')
print(mysql_account, mysql_password)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_account}:{mysql_password}@localhost:3306/database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
function = learning_project_function(db)

@app.route('/')
def index():
    #return function.test_user()
    return redirect('/login')

@app.route('/login')
def login_page():
	return render_template("login_page.html",**locals())

@app.route('/guest')
def guest_page():
	return render_template("guest_page.html",**locals())

@app.route('/chat')
def chat_page():
	apikey = request.cookies.get('apikey')
	character = request.args.get('character')
	print(f'chat_page apikey={apikey}, character={character}')
	return render_template("chat_page.html",**locals())

#need to load all the chat history
@app.route('/chat_history')
def chat_history():
	apikey = request.cookies.get('apikey')
	character = request.args.get('character')
	print(f'chat_page apikey={apikey}, character={character}')
	# notice db store data in single quote, and js should use double quote
    # so it should be transform here
	return jsonify(function.chat_history(apikey, character).replace("'",'"'))


#need to load all the chat history
@app.route('/new_chat',methods =['POST'])
def new_chat():
	chat = request.form.get('chat')
	apikey = request.cookies.get('apikey')	
	character = request.form.get('character')
	print(f'new_chat apikey={apikey}, character={character}, new_chat={new_chat}')
	function.new_chat(apikey, chat,character)
	return "OK"

@app.route('/character')
def character_select_page():
	apikey = request.cookies.get('apikey')
	print(f'character_page apikey={apikey}')
	return render_template("character_select_page.html",**locals())

@app.route('/setting')
def setting_page():
	return render_template("setting_page.html",**locals())






@app.route('/Project',methods =['POST'])
def login_post():	
	#username = request.form.get('username')
	email = request.form.get('email')
	password = request.form.get('password')
	user = function.login_check(email,password)
	if(user == -1):
		return jsonify({'status':'login_fail'})
	else:
		user_id = user[0]
		username = user[1]
		return jsonify({'status':'login_success','user_id':user_id,'username':username})

@app.route('/google_api',methods =['POST'])
def google_api():	
	#username = request.form.get('username')
	email = request.form.get('email')
	key = request.form.get('key')
	print(email,key)
	#check value in database
	
	return '{"login_result": "' + str(function.check_google_api(key)) + '"}'
	
if __name__ == "__main__":
    app.run(host='140.119.19.27', port=5000)

