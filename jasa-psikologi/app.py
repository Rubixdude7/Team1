from flask import Flask, render_template
import datetime
import models as db
from peewee import *

app = Flask(__name__)

year = datetime.datetime.now().year

db.user.select(db.user.user_id == 1)

@app.route('/')
def index():

    return render_template("index.html", year=year)


if __name__ == '__main__':
    app.run()
