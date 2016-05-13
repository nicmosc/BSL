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
    text = request.args.get('input_text')
    letters = list(text)

    print(letters)
    print(jsonify(letters))
    # we process the text here for now
    #return jsonify(result=a + b)

if __name__ == '__main__':
    # app.run(
    #     host='localhost',
    #     port=int("5000"),
    #     debug=True
    # )
	app.run()