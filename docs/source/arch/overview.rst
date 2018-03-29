Overview of the Web App's Architecture
======================================

The web app's source code is written in `Python 3`_ and uses the Flask_
web microframework. We use MySQL_ for all database operations because of
its reliability and speed.

.. _Python 3: https://www.python.org/
.. _Flask: http://flask.pocoo.org/
.. _MySQL: https://www.mysql.org/

Purpose of Each Python Script
-----------------------------

Three Python scripts perform most of the application's logic:

:doc:`/modules/app`
    This script starts the web server and sets up its URL routes.
    Additionally, the most of the logic of the web app happens here.
    
:doc:`/modules/models`
    This script defines *models* and *fields* for the database. It uses
    the peewee_ ORM to protect the web app from SQL injections.
    
:doc:`/modules/query`
    This script defines a class called :class:query.query which has
    convenient methods for accessing the database in a variety of ways.

.. _peewee: http://docs.peewee-orm.com/en/2.10.2/
