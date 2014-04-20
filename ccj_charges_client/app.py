"""
ccj_charges_client

Base server for ccj_charges_client
author: SC3
email: wilbertomorales777@gmail.com

"""

from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
