import logging

from text_unidecode import unidecode

from flask import render_template, flash, url_for, redirect, g, request, jsonify, current_app
from flask_login import login_required
from requests.utils import unquote

from app import db
from app.main import bp
from app.models import Recipe, Tag
from app.main.forms import AddRecipeForm, SearchForm

@bp.route("/")
def index():
    """
    This is the grocery list.
    Concatenates the ingredients from all the upcoming recipes
    The ingredients dict that we pass to the template has this structure
    {
        "carrot": {
            "g": 200,
            "number": 4,
            "str": "200g, 4number",
        },
        "salt": {
            "g": 20,
            "pinch": 3,
            "str": "20g, 3pinch",
        },
    }
    If two ingredients have the same unit, I add the quantities, but trying to
    unify all the different ways of expressing ingredient units would be a lost cause.
    We add the str key because doing formatting work in the template is so much fun
    """
    recipes = Recipe.query.filter_by(upcoming=True)
    ingredients = dict()
    for recipe in recipes:
        recipe_d = recipe.to_dict()
        for ingredient in recipe_d["ingredients"]:
            #worth changing the ingredients to a named tuple ?
            #would be better at least here
            name, unit, quantity = (ingredient["name"],
                                    ingredient["unit"],
                                    ingredient["quantity"])
            quantity = quantity * recipe.upcoming_servings / recipe.servings
            if name in ingredients:
                if unit in ingredients[name]:
                    ingredients[name][unit] += quantity
                else:
                    ingredients[name][unit] = quantity
            else:
                ingredients[name] = {
                        unit: quantity,
                }

    for name, d in ingredients.items():
        s = ", ".join("{:g}{}".format(
            round(quantity, 2), unit) for unit, quantity in d.items())
        ingredients[name]["str"] = s

    return render_template("grocery_list.html",
            title="Grocery list",
            recipes=recipes,
            ingredients=ingredients)

@bp.route("/recipes/")
def recipes():
    """
    List of all recipes
    """
    page = request.args.get("page", 1, type=int)

    recipes_paginated = Recipe.query.paginate(
            page=page,
            per_page=current_app.config["RECIPES_PER_PAGE"],
            error_out=False)
    recipes_d = [recipe.to_dict() for recipe in recipes_paginated.items]

    next_url = (url_for("main.recipes", page=recipes_paginated.next_num)
                if recipes_paginated.has_next
                else None)
    prev_url = (url_for("main.recipes", page=recipes_paginated.prev_num)
                if recipes_paginated.has_prev
                else None)

    return render_template("recipes.html",
                           title="Recipes",
                           recipes=recipes_d,
                           next_url=next_url,
                           prev_url=prev_url)

@bp.route("/recipes/add/", methods=["GET", "POST"])
@login_required
def add_recipe():
    form = AddRecipeForm()
    if form.validate_on_submit():
        #TODO create formtodict function ? then recipe = Recipe(**d)
        recipe = Recipe(
                name=form.name.data,
                steps=form.steps.data,
                servings=form.servings.data,
                upcoming_servings=form.servings.data,
                cooking_temperature=form.cooking_temperature.data,
                cooking_time=form.cooking_time.data,
                prep_time=form.prep_time.data,
        )
        ingredients = [ing for ing in form.ingredients.data
                if ing["ing_name"] and ing["quantity"] and ing["unit"]]
        # This key name conversion is needed because I cannot have a 'name'
        # attribute in IngredientForm, because I'm using it in a FieldList,
        # and WTForms already adds a name field in FieldList
        [ing.update({"name": ing.pop("ing_name")}) for ing in ingredients]

        recipe.add_ingredients(ingredients)
        recipe.add_tags()
        db.session.add(recipe)
        db.session.commit()
        flash(f"Recipe '{form.name.data}' added")
        return redirect(url_for("main.index"))
    return render_template("add_recipe.html", title="New recipe", form=form)

@bp.route("/recipes/<name>/")
def recipe(name):
    """
    Details of one recipe
    """
    recipe = Recipe.query.filter_by(name=unquote(name)).first_or_404()
    tags = [tag.name for tag in recipe.tags]
    return render_template("recipe.html",
            title=recipe.name,
            recipe=recipe.to_dict(),
            tags=", ".join(tags))

@bp.route("/recipes/<name>/edit/", methods=["GET", "POST"])
@login_required
def edit_recipe(name):
    """
    Most of the work is comparing old ingredients with new ones. Deleting
    quantities for the removed ingredients is handled by Recipe.delete_quantities,
    modifying quantities is handled by Recipe.add_ingredients method.
    We do not delete ingredients that become now unused from the database.
    """
    recipe = Recipe.query.filter_by(name=unquote(name)).first_or_404()
    recipe_d = recipe.to_dict()
    ing_d = [{"ing_name": ing["name"], "unit": ing["unit"], "quantity": ing["quantity"]}
            for ing in recipe_d["ingredients"]]
    form = AddRecipeForm(obj=recipe, ingredients=ing_d, original_name=recipe.name)
    if form.validate_on_submit():
        #TODO maybe add a Recipe.update method that loops over a dict with setattr?
        recipe.name = form.name.data
        recipe.steps = form.steps.data
        recipe.servings = form.servings.data
        recipe.cooking_temperature = form.cooking_temperature.data
        recipe.cooking_time = form.cooking_time.data
        recipe.prep_time = form.prep_time.data

        ingredients = [ing for ing in form.ingredients.data
                       if ing["ing_name"]
                       and ing["quantity"]
                       and ing["unit"]]
        [ing.update({"name": ing.pop("ing_name")}) for ing in ingredients]

        old_ingredient_names = {ing["ing_name"] for ing in ing_d}
        new_ingredient_names = {ing["name"] for ing in ingredients}
        recipe.delete_quantities(old_ingredient_names - new_ingredient_names)

        logging.debug(ing_d)
        logging.debug(ingredients)
        logging.debug(old_ingredient_names - new_ingredient_names)

        recipe.add_ingredients(ingredients)
        recipe.add_tags()
        db.session.add(recipe)
        db.session.commit()
        flash(f"Recipe '{recipe.name}' edited")
        return redirect(url_for("main.recipe", name=recipe.name))
    return render_template("add_recipe.html",
            title=f'{recipe_d["name"]} - editing',
            form=form)

@bp.route("/search/")
def search():
    """
    Search by tag only. You can exclude tags by prefixing them with '-'
    """
    if not g.search_form.validate():
        return redirect(url_for("main.recipes"))

    page = request.args.get("page", 1, type=int)

    query_string = g.search_form.query.data
    tags = query_string.split()
    tags = [unidecode(tag).lower() for tag in tags]

    #TODO : does one select per tag, no big deal, but see if there's better
    query = db.session.query(Recipe)
    for tag in tags:
        if tag.startswith("-"):
            query = query.filter(~Recipe.tags.any(Tag.name.contains(tag.lstrip("-"))))
        else:
            query = query.filter(Recipe.tags.any(Tag.name.contains(tag)))

    recipes_paginated = query.paginate(
            page=page,
            per_page=current_app.config["RECIPES_PER_PAGE"],
            error_out=False)
    recipes_d = [recipe.to_dict() for recipe in recipes_paginated.items]

    next_url = (url_for("main.search",
                        query=query_string,
                        page=recipes_paginated.next_num)
                if recipes_paginated.has_next
                else None)
    prev_url = (url_for("main.search",
                        query=query_string,
                        page=recipes_paginated.prev_num)
                if recipes_paginated.has_prev
                else None)

    return render_template("recipes.html",
            title="Recipes",
            recipes=recipes_d,
            prev_url=prev_url,
            next_url=next_url)

@bp.route("/add_upcoming/", methods=["POST"])
@login_required
def add_upcoming():
    recipe = Recipe.query.get_or_404(int(request.form["recipe_id"]))
    try:
        upcoming_servings = int(request.form["upcoming_servings"])
    except ValueError:
        pass
    else:
        recipe.upcoming_servings = upcoming_servings

    recipe.upcoming = True

    db.session.add(recipe)
    db.session.commit()

    return jsonify({"upcoming": True})

@bp.route("/remove_upcoming/", methods=["POST"])
@login_required
def remove_upcoming():
    recipe = Recipe.query.get_or_404(int(request.form["recipe_id"]))

    recipe.upcoming = False

    db.session.add(recipe)
    db.session.commit()

    return jsonify({"upcoming": False})

@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
