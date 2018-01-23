from flask import Flask, render_template
import datetime

app = Flask(__name__)

year = datetime.datetime.now().year


@app.route('/')
def index():

    return render_template("index.html", year=year)


if __name__ == '__main__':
    app.run()
