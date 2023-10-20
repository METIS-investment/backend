from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'This is the METIS investment API.'


if __name__ == '__main__':
    app.run()
