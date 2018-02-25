import pytest

from app import create_app, db
from config import TestConfig

@pytest.fixture
def set_db(request):
    app = create_app(TestConfig)
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    def teardown():
        db.session.remove()
        db.drop_all()
        app_context.pop()
    request.addfinalizer(teardown)
