import jwt, os, duo_client
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
   
   #keyVaultName = os.environ["KEY_VAULT_NAME"]
   #KVUri = f"https://{keyVaultName}.vault.azure.net"
   KVUri = f"https://duo-key-vault.vault.azure.net"
   credential = DefaultAzureCredential()
   client = SecretClient(vault_url=KVUri, credential=credential)
   duo_auth_ikey = client.get_secret("duo-auth-ikey").value
   duo_auth_skey = client.get_secret("duo-auth-skey").value
   duo_auth_api = client.get_secret("duo-auth-api").value
   
   #duo_admin_ikey = client.get_secret("duo-admin-ikey")
   #duo_admin_skey = client.get_secret("duo-admin-skey")
   #duo_admin_api = client.get_secret("duo-admin-api")
   
   duo_auth_client = duo_client.Auth(
      ikey = duo_auth_ikey,
      skey = duo_auth_skey,
      host = duo_auth_api
   )
   
   #duo_admin_client = duo_client.Admin(
   #   ikey = auth_ikey,
   #   skey = auth_skey,
   #   host = duo_auth_api
   #)
   
   ping_result = "None"
   
   try: 
      ping_result = duo_auth_client.ping()
   except Exception as e:
      print("custom error")
      print(e)
   
   headers = request.headers
   authorization = request.authorization
   data = request.data
   email = request.headers['X-Ms-Client-Principal-Name']
   
   id_token = request.headers['X-Ms-Token-Aad-Id-Token']
   
   id_alg = jwt.get_unverified_header(id_token)['alg']
   id_decoded = jwt.decode(id_token, algorithms=[id_alg], options={"verify_signature": False})
   
   id_token_email = id_decoded['email']
   
   access_token = request.headers['X-Ms-Token-Aad-Access-Token']
   
   access_alg = jwt.get_unverified_header(access_token)['alg']
   access_decoded = jwt.decode(access_token, algorithms=[access_alg], options={"verify_signature": False})
   
   print('Request for index page received')
   return render_template('index.html', headers = ping_result, authorization = id_decoded, data = id_token_email)

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
