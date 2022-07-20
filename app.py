import jwt
from aadtoken import get_public_key

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)

@app.route('/')
def index():
   headers = request.headers
   authorization = request.authorization
   data = request.data
   email = request.headers['X-Ms-Client-Principal-Name']
   id_token = request.headers['X-Ms-Token-Aad-Id-Token']
   
   public_key = get_public_key(id_token)
   
   decoded = jwt.decode(id_token, public_key, algorithms=["RS256"])
   
   print('Request for index page received')
   return render_template('index.html', headers = email, authorization = id_token, data = decoded)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
