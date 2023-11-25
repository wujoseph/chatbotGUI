from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, redirect, render_template, session, url_for, request, send_file
from bin.db_function import learning_project_function
import os.path
import logging
import json
import requests
from flask_oauthlib.client import OAuth

logging.basicConfig(filename="../serverlog/serverlog.log", 
					filemode='a',
					format='%(levelname)s - %(message)s',
					level=logging.INFO)
logging.info("START SERVER")


#read key from other file
path = os.path.join(os.path.dirname(__file__) ,'../key.json')
path = os.path.abspath(path)

with open(path,'r') as f:
	data = json.load(f)
	mysql_account = data["mysql_account"]
	mysql_password = data["mysql_password"]
	consumer_key = data["consumer_key"]
	consumer_secret = data["consumer_secret"]
	flask_secret_key = data["flask_secret_key"]

app = Flask(__name__,template_folder='template',static_url_path='', 
			static_folder='template/css')
app.secret_key = flask_secret_key

#MySQL database setting

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_account}:{mysql_password}@localhost:3306/database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Google Oauth API setting
oauth = OAuth(app)

google = oauth.remote_app(
	'google',
	consumer_key=consumer_key,
	consumer_secret=consumer_secret,
	request_token_params={
		'scope': 'email',
	},
	base_url='https://www.googleapis.com/oauth2/v1/',
	request_token_url=None,
	access_token_method='POST',
	access_token_url='https://accounts.google.com/o/oauth2/token',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
)

function = learning_project_function(db)

@app.route('/')
def index():
	#return function.test_user()
	return redirect('/login')

@app.route('/login')
def login_page():
	return render_template("login_page.html",**locals())

@app.route('/login/google')
def login_google():
	return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/google/authorized')
def authorized():
	response = google.authorized_response()
	if response is None or response.get('access_token') is None:
		return 'Access denied: reason={0} error={1}'.format(
			request.args['error_reason'],
			request.args['error_description']
		)
	session['access_token'] = response['access_token']
	user_info = google.get('userinfo')
	try:
		email = user_info.data['email']
		session['email'] = email
	except KeyError:
		print('keyerror:',user_info.data)
		logging.warning('keyerror in google email')
		return ""

	# 如果不存在帳號，先註冊
	# TO DO: insert new row in user table
	if(not user_cookie_check(email)):
		pass

	# 如果認證成功，重定向到chat_page

	# return the email and write cookie in frontend
	# then redirect by js
	# maybe try callback
	return redirect('/character')

@google.tokengetter
def get_google_oauth_token():
	return session.get('access_token')


@app.route('/guest')
def guest_page():
	return render_template("guest_page.html",**locals())

@app.route('/chat')
def chat_page():
	email = session['email'] 
	if(not user_cookie_check(email)):
		return redirect('/notlogin')
	else:
		return render_template("chat_page.html",**locals())

@app.route('/chat2')
def chat_page2():
	apikey = request.cookies.get('apikey')
	character = request.args.get('character')
	#print(f'chat_page apikey={apikey}, character={character}')
	return render_template("chat_page2.html",**locals())


#need to load all the chat history
@app.route('/chat_history')
def chat_history():
	email = session['email'] 
	character = request.args.get('character')

	# notice db store data in single quote, and js should use double quote
	# so it should be transform here

	try:
		response = function.chat_history(email, character).replace("'",'"')
	except AttributeError:# if there is no chat history, then replace function will cause this error
		response = ""
	return jsonify(response)


#need to load all the chat history
@app.route('/new_chat',methods =['POST'])
def new_chat():
	chat = request.form.get('chat')
	email = session['email'] 
	character = request.form.get('character')
	#print(f'new_chat apikey={apikey}, character={character}, new_chat={new_chat}')
	logging.info(f'new_chat email={email}, character={character}, new_chat={new_chat}')
	function.new_chat(email, chat,character)
	return "OK"

@app.route('/character')
def character_select_page():
	email = session['email'] 
	if(not user_cookie_check(email)):
		return redirect('/notlogin')
	else:
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
	#print(email,key)
	#check value in database
	
	return jsonify({"login_result":str(function.check_google_api(key)), "email":email})

# call tts reference api
@app.route('/generate_audio',methods =['POST'])
def generate_audio():
	text = request.form.get('text')
	if(len(text) > 100):
		text = text[0:100]#cap the text
	url = 'http://127.0.0.1:7860/run/predict/'
	data = {"fn_index":0,"data":[text,"human","简体中文",1]}
	x = requests.post(url, json = data)
	file_name = 'OK'
	try:
		response = json.loads(x.text)
		file_name = response["data"][1]["name"]
	except:
		logging.warning(f"error audio response:,{response}")
	return file_name

# return audio file(wav)
@app.route('/audio')
def audio():
	filename = request.args.get('file')
	#print(filename)
	return send_file(filename)

@app.route('/notlogin')
def notlogin():
	# TO DO: new html page
	return render_template("notlogin.html",**locals())

# check login status, if user had login, they should have cookie
def user_cookie_check(email)->bool:
	if((email is None) or email == ""):
		return False
	return function.check_google_email(email)

if __name__ == "__main__":
	path1 = os.path.join(os.path.dirname(__file__) ,'../ssltest/personabot.site_key.txt')
	path1 = os.path.abspath(path1)
	path2 = os.path.join(os.path.dirname(__file__) ,'../ssltest/personabot.site.crt')
	path2 = os.path.abspath(path2)
	app.run(host='140.119.19.27', port=443,ssl_context=(path2,path1))

