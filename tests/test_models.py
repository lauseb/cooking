from itertools import chain

from text_unidecode import unidecode

from app import db
from app.models import Ingredient, Quantity, Recipe, Tag

def test_ingredient(set_db):
    names = {"test", "çéàü", "1234"}
    for name in names:
        ingredient = Ingredient(name=name)
        db.session.add(ingredient)
    db.session.commit()

    ingredients = Ingredient.query.all()
    assert names == set(ingredient.name for ingredient in ingredients)

def test_recipe_add(set_db):
    name = "eau salée"
    recipe = Recipe(name=name)

    db.session.add(recipe)
    db.session.commit()

    assert len(Recipe.query.all()) == 1
    assert Recipe.query.all()[0].name == name

def test_recipe_add_ingredients(set_db):
    #TODO warning here when we add "eau" for the second time,
    # when adding the quantity in add_ingredients. Try to fix that ?
    ingredients_eausel = [
            {"name": "eau", "quantity": 1, "unit": "L"},
            {"name": "sel", "quantity": 10, "unit": "g"}]

    ingredients_eaupoivre = [
            {"name": "eau", "quantity": 2, "unit": "mL"},
            {"name": "poivre", "quantity": 10, "unit": "g"}]

    recipe_eausel = Recipe(name="eau salée")
    recipe_eausel.add_ingredients(ingredients_eausel)

    db.session.add(recipe_eausel)
    db.session.commit()

    recipe_eaupoivre = Recipe(name="eau poivrée")
    recipe_eaupoivre.add_ingredients(ingredients_eaupoivre)

    db.session.add(recipe_eaupoivre)
    db.session.commit()

    assert len(Ingredient.query.all()) == 3
    assert len(Quantity.query.all()) == 4

def test_recipe_add_tags(set_db):
    #TODO warning here when we add "eau" for the second time,
    # when adding the quantity in add_ingredients. Try to fix that ?
    ingredients_eausel = [
            {"name": "eau", "quantity": 1, "unit": "L"},
            {"name": "sel", "quantity": 10, "unit": "g"}]

    ingredients_eaupoivre = [
            {"name": "eau", "quantity": 2, "unit": "mL"},
            {"name": "poivre", "quantity": 10, "unit": "g"}]

    recipe_eausel = Recipe(name="eau salée")
    recipe_eausel.add_ingredients(ingredients_eausel)
    recipe_eausel.add_tags()

    db.session.add(recipe_eausel)
    db.session.commit()

    recipe_eaupoivre = Recipe(name="eau poivrée")
    recipe_eaupoivre.add_ingredients(ingredients_eaupoivre)
    recipe_eaupoivre.add_tags()

    db.session.add(recipe_eaupoivre)
    db.session.commit()

    expected_tags = {unidecode(ingredient["name"]).lower()
            for ingredient in chain(ingredients_eausel, ingredients_eaupoivre)}
    expected_tags.update(unidecode(elem).lower() for elem in recipe_eausel.name.split())
    expected_tags.update(unidecode(elem).lower() for elem in recipe_eaupoivre.name.split())
    assert expected_tags == set(tag.name for tag in Tag.query)
    assert len(Tag.query.filter_by(name="eau").first().recipes) == 2
    assert len(Tag.query.filter_by(name="sel").first().recipes) == 1
    assert len(Tag.query.filter_by(name="salee").first().recipes) == 1

def test_recipe_delete_quantities(set_db):
    ingredients = [
            {"name": "eau", "quantity": 1, "unit": "L"},
            {"name": "foo", "quantity": 4, "unit": "a"},
            {"name": "bar", "quantity": 9, "unit": "b"},
            {"name": "sel", "quantity": 10, "unit": "g"}]

    recipe = Recipe(name="eau salée")
    recipe.add_ingredients(ingredients)

    db.session.add(recipe)
    db.session.commit()

    assert len(Ingredient.query.all()) == 4
    assert len(Quantity.query.all()) == 4
    recipe.delete_quantities(["foo", "bar"])
    assert len(Ingredient.query.all()) == 4
    assert len(Quantity.query.all()) == 2

def test_recipe_todict(set_db):
    ingredients = [
            {"name": "eau", "quantity": 1, "unit": "L"},
            {"name": "sel", "quantity": 10, "unit": "g"}]

    recipe_creation_dict = {
            'name': 'eau salée',
            'id': 1,
            'steps': "test steps",
            'upcoming': True,
            'upcoming_servings': 5,
            'servings': 2,
            'cooking_temperature': 150,
            'prep_time': 20,
            'cooking_time': 40,
    }

    recipe_dict = recipe_creation_dict.copy()
    recipe_dict["ingredients"] = ingredients

    recipe = Recipe(**recipe_creation_dict)
    recipe.add_ingredients(ingredients)
    recipe.add_tags()

    db.session.add(recipe)
    db.session.commit()

    assert recipe.to_dict() == recipe_dict

#TODO get over routes, and test some scenarios, like editing a recipe...
