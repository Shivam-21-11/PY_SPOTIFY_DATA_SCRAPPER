from flask import Flask,request,jsonify
from flask import url_for , redirect
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World"

@app.route('/callback')
def get_code():
    auth_code = request.args.get('code')
    if auth_code:
        return auth_code
    else:
        return 'Auth Failed'



if __name__=="__main__":
    app.run(port=8080,debug=True,use_reloader=False)