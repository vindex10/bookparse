BookParser
==========

Recognize types of pages in book, then parse them and put data into DB

#Installation

How to run an example?
----------------------

Installation consists of a few simple steps:

* Install git, and clone repo
* Install python, and virtualenv. Initialize virtualenv in repo. Activate
* Create MySQL database. Create DB. Import [dump](https://bitbucket.org/vindex10/bookparse/downloads/bookdata.dump.tgz)
* Copy /config/dbmanager.config from default one. Fill requisites.
* Put pdf named book1.pdf in "/data" dir. [Book for testing](https://bitbucket.org/vindex10/bookparse/downloads/book1.pdf)
* Now simply run: python manage.py 1 --pages 1-2 --exclude 2

You should have python3 installed.
Dependencies are saved at requirements.txt.
To install them with pip:

    pip install --upgrade pip #to upgrade pip
    pip install -r requirements.txt

How does it work?
-----------------

You manually add book to DB, then taking the ID, rename your book into the form: bookID.pdf (for example book12.pdf, if ID is 12). Your book consists of different types of pages. For each type of page you must write **recognizer**, which will return True if page recognized by it. Put recognizer to "/recognizers/bookID.py". Pay attention to __add_type__ function, it is important. Examples of structure of recognizers you can find now in repo. Each recognizer has own id, and after recognition, id will be passed to **parser**. Parser loads a collection of parsers for specific book, then runs parser for special page type (by ID). Parser returns collection of dictionaries, each corresponds to one item. Then DBManager put all items to DB.items.


*Images correspondence* Images in html (pages.pagedata) are compared one-by-one to those in items table by md5 hash. Paths are in form "items.ID" if ID is defined, or "undefined", if there is no such image among items.

To do
-----
* Improve help :)
