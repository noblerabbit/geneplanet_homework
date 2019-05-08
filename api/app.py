import sys
sys.path.append("../")
import prs_calculator
import numpy as np
import pandas as pd

import time
from flask import Flask, Response, stream_with_context

#
def callback(statement):
    print("here")
    # yield statement
    yield from deeper()
    
def deeper():
    yield "Deeper"

app = Flask(__name__)

@app.route('/')
def main():
    return '''<div>Start</div>
    <script>
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/stream', true);
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

app.run(debug=True, port=5000, host='0.0.0.0')
