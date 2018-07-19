from utilities import Encryption
import requests

url_login = 'uggcf://jjj.fvyireqnqqvrf.pbz'
username = 'ybbxvat123nop'
password = 'Dr6rh3ie!'

payload = {'username': Encryption.decrypt(username), 'password': Encryption.decrypt(password)}
request = requests.post(Encryption.decrypt(url_login), data=payload)
print request.content