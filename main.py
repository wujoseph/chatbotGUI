from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect

from flask import render_template
#from bin.db_function import learning_project_function

app = Flask(__name__,template_folder='template',static_url_path='', 
            static_folder='template/css')


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
	return render_template("chat_page.html",**locals())






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

if __name__ == "__main__":
    app.run()

