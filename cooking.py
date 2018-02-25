from app import create_app, db
from app.models import User, Ingredient, Recipe, Quantity, Tag

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"db": db,
            "User": User,
            "Ingredient": Ingredient,
            "Recipe": Recipe,
            "Quantity": Quantity,
            "Tag": Tag,
            }
