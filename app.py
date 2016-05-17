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
import json

# Initialize the Flask application
app = Flask(__name__)


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
def processText():
    text = request.args.get('input_text', '', type = str)
    letters = list(text.upper())

    data = []   # will contain the signs/letters with their path

    for letter in letters:
        obj = {}
        obj['name'] = letter
        obj['path'] = 'alphabet'    # specific to this program (will have to differentiate facial and more)
        data.append(json.dumps(obj))

    print(letters, data)
    #print(jsonify(letters))
    # we process the text here for now
    return jsonify(result=data)

if __name__ == '__main__':
    # app.run(
    #     host='localhost',
    #     port=int("5000"),
    #     debug=True
    # )
	app.run()