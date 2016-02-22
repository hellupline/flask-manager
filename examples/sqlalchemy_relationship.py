"""
Flask-manager.ext.sqalchemy.crud build a form for model,
but its a simple wtforms_alchemy, it does not add a relationship field.
I do not have any concrete idea how to add relationship fields,
I had this, but it got confuse, so I removed until I plan a better way.
"""
from wtforms_alchemy import ModelForm, fields as sa_fields
import sqlalchemy as sa
from sqlalchemy import orm
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_manager import crud as crud_
from flask_manager.ext.sqlalchemy import crud as sa_crud


db = SQLAlchemy()


class ModelA(db.Model):
    __tablename__ = 'model_a'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)


class ModelB(db.Model):
    __tablename__ = 'model_b'
    id = sa.Column(sa.Integer(), primary_key=True)
    a_id = sa.Column(sa.ForeignKey(ModelA.id), nullable=False)
    a = orm.relationship(ModelA, backref='b')
    name = sa.Column(sa.String(255), nullable=False, index=True)


class FormB(ModelForm):
    # pylint: disable=no-member
    a = sa_fields.QuerySelectField(query_factory=lambda: ModelA.query)

    class Meta:
        model = ModelB


class CrudA(sa_crud.SQLAlchemyCrud):
    db_session = db.session
    model = ModelA


class CrudB(sa_crud.SQLAlchemyCrud):
    db_session = db.session
    model = ModelB
    form_class = FormB


def main():
    # SQLAlchemyCrud support passing model, session through kwargs
    tree = crud_.Index(name='Example', url='', items=[
        CrudA(),
        CrudB(),
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
