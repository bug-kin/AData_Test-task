import json

import xmltodict
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def take_json_get_xml():
    record = json.loads(request.data)
    return xmltodict.unparse(record, encoding='utf-8')


if __name__ == '__main__':
    app.run()
