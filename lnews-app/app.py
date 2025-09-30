from flask import Flask, render_template
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/health')
def health():
    IPAddr = socket.gethostbyname(socket.gethostname())
    return {"hostname": IPAddr}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)