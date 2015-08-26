from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative

from le_crud.ext.sqlalchemy import (
    filters as sa_filters,
    scaffold as sa_scaffold,
)

# engine = create_engine('postgresql://mucca:oiuy0987@localhost/shop')
engine = create_engine('sqlite:////tmp/le_crud.db')
metadata = MetaData(bind=engine)
Session = scoped_session(sessionmaker(bind=engine))

metadata.create_all()


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

    def __str__(self):
        return self.name


tagkind_crud = sa_scaffold.build_crud(TagKind, db_session=Session)
tag_controller = sa_scaffold.build_controller(
    Tag, db_session=Session,
    filters=OrderedDict([
        ('search', sa_filters.SearchFilter([Tag.name, Tag.rules])),
        ('name', sa_filters.ColumnFilter(Tag.name)),
        ('kind', sa_filters.JoinColumnFilter(TagKind.name, TagKind)),
    ]),
    actions=OrderedDict([('print ids', print)])
)
tag_display = sa_scaffold.build_display(Tag)
