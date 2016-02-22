import sqlalchemy as sa
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_manager import crud as crud_
from flask_manager.ext.sqlalchemy import crud as sa_crud


db = SQLAlchemy()


class Model(db.Model):
    __tablename__ = 'model'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)


class Crud(sa_crud.SQLAlchemyCrud):
    db_session = db.session
    model = Model


def main():
    # SQLAlchemyCrud support passing model, session through kwargs
    tree = crud_.Index(name='Example', url='', items=[
        sa_crud.SQLAlchemyCrud(
            name='Example', db_session=db.session, model=Model),
        Crud(),
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
