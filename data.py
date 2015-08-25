from collections import OrderedDict
from wtforms.ext.sqlalchemy.fields import QuerySelectField
# , QuerySelectMultipleField
from wtforms_alchemy import ModelForm

import sqlalchemy as sa
from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative

from le_crud.ext.sqlalchemy import (
    controller as sa_controller, filters as sa_filters)
from le_crud import display, rules

# engine = create_engine('postgresql://mucca:oiuy0987@localhost/shop')
engine = create_engine('sqlite:////tmp/le_crud.db')
metadata = MetaData(bind=engine)
Session = scoped_session(sessionmaker(bind=engine))


class SessionModelForm(ModelForm):
    @classmethod
    def get_session(cls):
        return Session


@as_declarative(metadata=metadata)
class Base:
    __abstract__ = True
    query = Session.query_property()


class TagKind(Base):
    __tablename__ = 'tag_kind'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)

    def __str__(self):
        return self.name


class Tag(Base):
    __tablename__ = 'tag'
    id = sa.Column(sa.Integer(), primary_key=True)
    kind_id = sa.Column(sa.Integer, sa.ForeignKey('tag_kind.id'))
    kind = orm.relationship('TagKind', backref='tags')
    name = sa.Column(sa.String(255), nullable=False, index=True)
    rules = sa.Column(sa.Text, nullable=True)
    rules_expr = sa.Column(sa.Text)


class KindForm(SessionModelForm):
    class Meta:
        model = TagKind


class TagForm(SessionModelForm):
    kind = QuerySelectField(
        'Kind', query_factory=lambda: TagKind.query, allow_blank=True)

    class Meta:
        model = Tag


tagkind_controller = sa_controller.SQLAlchemyController(
    db_session=Session, model_class=TagKind, form_class=KindForm,
)
tagkind_display = display.Display(
    list=rules.ColumnSet(['id', 'name']),
    create=[rules.Form()],
    read=rules.FieldSet(['name']),
    update=[rules.Form()],
    delete=rules.FieldSet(['name']),
)


tag_controller = sa_controller.SQLAlchemyController(
    db_session=Session, model_class=Tag, form_class=TagForm,
    filters=OrderedDict([
        ('search', sa_filters.SearchFilter([Tag.name, Tag.rules])),
        ('name', sa_filters.ColumnFilter(Tag.name)),
        ('kind', sa_filters.JoinColumnFilter(TagKind.name, TagKind)),
    ]),
    actions=OrderedDict([
        ('print ids', print),
    ])
)
tag_display = display.Display(
    list=rules.ColumnSet(['id', 'name', 'rules']),
    create=[rules.Form()],
    read=rules.FieldSet(['name', 'rules']),
    update=[rules.Form()],
    delete=rules.FieldSet(['name', 'rules']),
)


metadata.create_all()
