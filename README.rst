Cooking
#######

Reasons why this exists
***********************

We cook everything we eat, every day. And each time we plan the trip to the supermarket, the same dreaded question arises : "What do we eat ?"

So each time, we think about some meals we want to have, and check for the recipes on some unkown website ("I thought I had saved that somewhere"), and since then the blog closed, and also we modified the recipe, but don't remember what was the modification, and also in our oven 180° was better than 195°, and it says it is for 4 persons but we do it as a main dish and it's barely enough for 2...

Yeah, first-world problems.

So, what does your thing do ?
*****************************

Basically, it allows you to think in terms of which meal you want to eat, instead of which ingredients you need to buy.

You first have to enter your recipes on the app, with the ingredients, steps, cooking time, heating temperature, servings...

Once that is done, you can add recipes to the upcoming recipe list. That generates you a grocery list, which adds together all the ingredients you need to buy.

You can search for recipes by tags (which you can include or exclude). Most tags are generated from the recipe's name, and the ingredients.

The boring description
**********************

It's a python/flask app, for self-hosting use. It works only with python >=3.6 . If you replace the ~10 f-strings I've used, it should work with most (all ?) 3.x versions.

It uses by default a SQLite db, with SQLAlchemy ORM. Check requirements.txt for the other librairies that it uses. If you want to use another db, just put the corresponding settings into config.py.

Installation / usage
********************

Clone the repo. Change the config in ``config.py``. You can create a ``env`` file to store environment variables (except ``FLASK_APP``). You might also want to suit the logger for your needs, in ``app/__init__.py``.

Install the requirements (you should probably set up a virtualenv before).

Set the ``FLASK_APP`` environment variable to ``path/to/cooking.py``. Configure the db by running ``flask db upgrade``.

Then execute ``flask run`` with your favorite wsgi server.

You might want to enable at least temporarily ``ALLOW_USER_REGISTRATION`` to register a couple users for the first time. Alternatively, fire up the flask shell (``flask shell``) and run :

.. code-block:: python

  >>> user = User(username="John")
  >>> user.set_password("hunter2")
  >>> db.session.add(user)
  >>> db.session.commit()

Upcoming features
*****************

* custom tags
* add some js spices like auto-suggest existing ingredients or tags
* ability to import recipes from usual recipes websites
* backup/restore
* at some point, an android checklist app
