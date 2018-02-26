import logging

from text_unidecode import unidecode

from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

recipe_tags = db.Table("recipe_tags",
        db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    quantity = db.relationship("Quantity", backref="ingredient", lazy="dynamic")

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"

class Recipe(db.Model):
    """
    Main model.
    Workflows :
      * when you want to add a new one, create an instance, then call
        add_ingredients, then add_tags.
      * when you want to edit one, change the fields, then delete the
        obsolete quantities with delete_quantities, then call add_ingredients.
        It will update the quantities too. Then call add_tags.

    TODO call add_ingredients and add_tags in the init ?
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    steps = db.Column(db.UnicodeText())
    servings = db.Column(db.Integer, default=1)
    cooking_temperature = db.Column(db.Integer)
    cooking_time = db.Column(db.Integer)
    prep_time = db.Column(db.Integer)
    upcoming = db.Column(db.Boolean, index=True, default=False)
    upcoming_servings = db.Column(db.Integer, default=1)

    quantities = db.relationship("Quantity", backref="recipe", lazy="dynamic")
    tags = db.relationship("Tag", secondary=recipe_tags, backref="recipes")

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"

    def add_tags(self):
        self.tags.clear()
        tag_names = set(unidecode(s.lower()) for s in self.name.split())
        tag_names.update(unidecode(quantity.ingredient.name.lower())
                         for quantity in self.quantities)

        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
            self.tags.append(tag)

    def add_ingredients(self, ingredients):
        #TODO rename this, it's more synchronise_ingredients than add_
        """
        We assume here that ingredients has been already checked
        ingredients = [
            {"name": "carrot", "quantity": 5, "unit": "kg"},
            ...
        ]
        """
        for ingredient in ingredients:
            ing = Ingredient.query.filter_by(name=ingredient["name"]).first()
            if ing is None:
                ing = Ingredient(name=ingredient["name"])
            # This little dance is to avoid a warning message by sqlalchemy.
            # If we don't check for ing.id before querying Quantity, it complains that
            # we query with a None id, whose behavior might change in future versions.
            quantity = None
            if ing.id:
                quantity = Quantity.query.filter_by(ingredient=ing, recipe=self).first()
                if quantity:
                    quantity.unit = ingredient["unit"]
                    quantity.quantity = ingredient["quantity"]
            if not quantity:
                quantity = Quantity(
                        unit=ingredient["unit"],
                        quantity=ingredient["quantity"],
                        ingredient=ing,
                        recipe=self
                )

    def delete_quantities(self, names):
        """
        When editing a recipe, you want to remove the quantities no longer used.
        names is an iterable containing all the ingredients' names whose quantities
        you want to remove
        """
        #TODO do only one ingredient query, and then use the relationship instead of
        # querying for the quantity
        for name in names:
            ing = Ingredient.query.filter_by(name=name).first()
            quantity = Quantity.query.filter_by(ingredient=ing, recipe=self).first()
            if quantity:
                db.session.delete(quantity)

    def to_dict(self):
        """
        return the recipe as dict following the usual structure
        {
            "name": str,
            "id": int,
            "upcoming": bool,
            "upcoming_servings": int,
            "steps": str,
            "servings": int,
            "cooking_temperature": int,
            "cooking_time": int,
            "prep_time": int,
            "ingredients": [
                {"name": name, "quantity": quantity, "unit": unit},
                ...
                ]
        }
        """
        ingredients = self.query.join(
                Quantity, self.id == Quantity.recipe_id
                ).join(
                        Ingredient,
                        Quantity.ingredient_id == Ingredient.id
                ).filter(
                        Recipe.id == self.id
                ).with_entities(
                        Ingredient.name,
                        Quantity.unit,
                        Quantity.quantity,
                ).all()
        logging.debug(ingredients)
        ingredients_list = [
                {
                    "name": ingredient.name,
                    "unit": ingredient.unit,
                    "quantity": ingredient.quantity,
                }
                for ingredient in ingredients]
        result = {
            "name": self.name,
            "id": self.id,
            "upcoming": self.upcoming,
            "upcoming_servings": self.upcoming_servings,
            "steps": self.steps,
            "servings": self.servings,
            "cooking_temperature": self.cooking_temperature,
            "cooking_time": self.cooking_time,
            "prep_time": self.prep_time,
            "ingredients": ingredients_list,
        }

        return result

    def delete(self):  # TODO
        """
        Remove this recipe.
        If clean=True, remove all the orphan ingredients and quantities
        """
        pass

class Quantity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(32))
    quantity = db.Column(db.Integer)

    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))

    def to_dict(self):
        return {"name": self.ingredient.name,
                "quantity": self.quantity,
                "unit": self.unit}

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.ingredient.name} {self.quantity}{self.unit}'>"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.username}'>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
