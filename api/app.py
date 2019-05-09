import sys
sys.path.append("../")
import prs_calculator
import numpy as np
import pandas as pd

import time
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"


@app.route('/xml')
def main():
    return '''<div>Start</div>
    <script>
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/stream/HG00099', true);
        xhr.onreadystatechange = function(e) {
            var div = document.createElement('div');
            div.innerHTML = '' + this.readyState + ':' + this.responseText;
            document.body.appendChild(div);
        };
        xhr.send();
    </script>
    '''
    
@app.route('/stream/<sample_name>', methods=['GET'])
def streamed_response(sample_name):
    if sample_name not in ["HG00099"]:
        return "Please provide a valid sample name"
    def generate():
        yield "<h2>Calculating the PRS score for the sample: {}</h2><br>".format(sample_name)
        yield from prs_calculator.get_prs(sample_name)
    return Response(stream_with_context(generate()), mimetype = "text/html")

@app.route('/test')
def test():
    return "HELLO"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
