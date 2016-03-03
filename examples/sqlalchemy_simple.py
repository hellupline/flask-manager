import sqlalchemy as sa
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_manager import tree as tree_
from flask_manager.ext import sqlalchemy


db = SQLAlchemy()


class Model(db.Model):
    __tablename__ = 'model'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)


class Controller(sqlalchemy.SQLAlchemyController):
    db_session = db.session
    model_class = Model


def main():
    # SQLAlchemyCrud support passing model, session through kwargs
    tree = tree_.Index(name='Example', url='', items=[
        sqlalchemy.SQLAlchemyController(
            name='Example', db_session=db.session, model_class=Model),
        Controller(),
    ])
    app = Flask(__name__)

    db.init_app(app)
    db.app = app
    db.create_all()

    app.register_blueprint(tree.create_blueprint())
    app.config['SECRET_KEY'] = 'super-secret'
    app.run(debug=True)


if __name__ == '__main__':
    main()
