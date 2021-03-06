# In this example we are going to create a simple HTML
# page with 2 input fields (numbers), and a link.
# Using jQuery we are going to send the content of both
# fields to a route on our application, which will
# sum up both numbers and return the result.
# Again using jQuery we'l show the result on the page


# We'll render HTML templates and access data sent by GET
# using the request object from flask. jsonigy is required
# to send JSON as a response of a request

from flask import Flask, render_template, request, jsonify
from static.py.analyser import Analyser
from static.py.utils import list_files
import sys
from os import devnull

# Initialize the Flask application
app = Flask(__name__)

# Initalise the translating analyser
analyser = Analyser(app=True)

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('indexPage.html')

# Route that will process the AJAX request, sum up two
# integer numbers (defaulted to zero) and return the
# result as a proper JSON response (Content-Type, etc.)
@app.route('/_process_text')
def process_text():

    text = request.args.get('input_text', '', type = str)

    print text

    sys.stdout = open(devnull, 'w') # suppress printing from the result method
    data = analyser.process(text)
    sys.stdout = sys.__stdout__     # reset printing

    print 'Gloss:',data[0]
    print 'HTML:',data[1]
    print 'JS:',data[2]

    # return jsonify(result=data)

    return jsonify(result=(data[1],data[2]))

@app.route('/_print_dir')
def print_dir():
    res = list(list_files('static/res/animations'))
    return jsonify(result=res)

if __name__ == '__main__':
    # app.run(
    #     host='localhost',
    #     port=int("5000"),
    #     debug=True
    # )
	app.run()