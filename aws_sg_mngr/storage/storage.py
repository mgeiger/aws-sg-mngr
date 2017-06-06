import os
from flask import Flask
app = Flask(__name__)

db_type = None

@app.route('/')
def hello_world():
    global db_type
    return "Hello World: {}".format(db_type)

if __name__ == '__main__':
    global db_type
    db_type = "Matt"
    #db_type = os.environ['AWS_SG_DATABASE']
    app.run()
