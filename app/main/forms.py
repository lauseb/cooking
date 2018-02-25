from flask import request
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField,
        FieldList, FormField, IntegerField)
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from app.models import Recipe

class IngredientForm(FlaskForm):
    #TODO using name instead of ing_name would be better
    #but it fails because FieldList already adds a name attribute
    ing_name = StringField("Ingredient", validators=[Length(min=0, max=100)])
    quantity = StringField("Quantity", validators=[Length(min=0, max=100)])
    unit = StringField("Unit", validators=[Length(min=0, max=100)])

    #Have to disable csrf protection for this form, we already have one
    def __init__(self, *args, **kwargs):
        kwargs["csrf_enabled"] = False
        super(IngredientForm, self).__init__(*args, **kwargs)

    #TODO
    #I feel like there's gotta be a better approach for this
    #Probably a custom validator in AddRecipeForm ?
    def validate_ing_name(self, ing_name):
        if (self.unit.data or self.quantity.data) and not ing_name.data:
            raise ValidationError("Field missing")

    def validate_quantity(self, quantity):
        if (self.ing_name.data or self.unit.data) and not quantity.data:
            raise ValidationError("Field missing")

    def validate_unit(self, unit):
        if (self.ing_name.data or self.quantity.data) and not unit.data:
            raise ValidationError("Field missing")

class AddRecipeForm(FlaskForm):
    name = StringField("Recipe name", validators=[DataRequired()])
    steps = TextAreaField("Steps")
    servings = IntegerField("Servings", validators=[DataRequired()])
    cooking_temperature = IntegerField("Cooking temperature", validators=[Optional()])
    prep_time = IntegerField("Preparation time", validators=[Optional()])
    cooking_time = IntegerField("Cooking time", validators=[Optional()])
    ingredients = FieldList(FormField(IngredientForm), min_entries=20)
    submit = SubmitField("Submit")

    def __init__(self, original_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        #TODO add url validation (we don't want /:? etc characters here)
        if name.data != self.original_name:
            recipe = Recipe.query.filter_by(name=name.data).first()
            if recipe:
                raise ValidationError("Recipe exists already")

    def validate_servings(self, servings):
        if servings < 1:
            raise ValidationError("Servings must be at least one")

    def validate_ingredients(self, ingredients):
        for ingredient in ingredients:
            if ingredient.ing_name.data:
                break
        else:
            raise ValidationError("Please fill at least one ingredient")


class SearchForm(FlaskForm):
    query = StringField('Find a recipe', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
