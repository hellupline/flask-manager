from contextlib import contextmanager
from itertools import chain
from cached_property import cached_property
from wtforms_alchemy import ModelForm
import sqlalchemy as sa

from flask_manager import controller, display_rules as display_rules_


def unique(items):
    done = set()
    for item in items:
        if item in done:
            continue
        done.add(item)
        yield item


class SearchFilter(controller.SearchFilter):
    def __init__(self, columns, join_tables=None):
        self.columns = columns
        self.join_tables = join_tables

    def filter(self, value, query):
        clauses = [column.contains(value) for column in self.columns]
        return query.filter(sa.or_(*clauses))


class FieldFilter(controller.FieldFilter):
    def __init__(self, column, join_tables=None):
        # I know its evil, and bad, but will inject session in
        # SQLAlchemyController.__ini__
        self.db_session = None
        self.column = column
        self.join_tables = join_tables

    def filter(self, value, query):
        return query.filter(self.column == value)

    def get_choices(self):
        values = self.db_session.query(self.column).distinct()
        for value in chain.from_iterable(values):
            title = str(value).capitalize()
            if isinstance(value, bool):
                value = str(int(value))
            yield value, title


@contextmanager
def transaction(db_session):
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


def get_model_name(model_class):
    return sa.inspect(model_class).entity.__name__


def get_columns(model_class):
    columns = sa.inspect(model_class).columns
    return [
        key for key, column in columns.items()
        if not (column.primary_key or column.foreign_keys)
    ]


class SQLAlchemyController(controller.Controller):
    extra_display_rules = {}
    db_session = None
    model_class = None

    def __init__(self, *args, db_session=None, model_class=None, **kwargs):
        if db_session is not None:
            self.db_session = db_session
        if model_class is not None:
            self.model_class = model_class

        if self.name is None:
            self.name = get_model_name(self.model_class)

        for filter_ in self.filters.values():
            filter_.db_session = self.db_session
        super().__init__(*args, **kwargs)

    # {{{ Generated from model_class
    @cached_property
    def form_class(self):
        class Form(ModelForm):
            @classmethod
            def get_session(cls):
                return self.db_session

            class Meta:
                model = self.model_class
        return Form

    @cached_property
    def display_rules(self):
        fields = get_columns(self.model_class)
        return {
            'list': display_rules_.ColumnSet(fields),
            'create': display_rules_.SimpleForm(),
            'read': display_rules_.DataFieldSet(fields),
            'update': display_rules_.SimpleForm(),
            'delete': display_rules_.DataFieldSetWithConfirm(fields),
            **{
                key: self.extra_display_rules['form']
                for key in ('create', 'update')
                if 'form' in self.extra_display_rules
            },
            **self.extra_display_rules,
        }
    # }}}

    # {{{ Helpers
    def get_query(self):
        return self.db_session.query(self.model_class)

    def new(self):
        # pylint: disable=not-callable
        return self.model_class()

    def save(self, item):
        with transaction(self.db_session) as session:
            session.add(item)
        return item

    def delete(self, item):
        with transaction(self.db_session) as session:
            session.delete(item)

    def count(self, query):
        # sqlalchemy query.count() uses a generic subquery count, which
        # is slow, this one only replace the selected columns with a
        # COUNT(*)
        stmt = query.statement.with_only_columns([sa.func.count()])
        return self.db_session.execute(stmt).scalar()

    def _get_field(self, name):
        if name[0] == '-':
            return -getattr(self.model_class, name[1:])
        return getattr(self.model_class, name)

    def _filter(self, query, filters):
        join_tables = []
        for filter_, value in self.get_filters(filters):
            if filter_.join_tables is not None:
                join_tables.extend(filter_.join_tables)
            query = filter_.filter(value, query)
        if join_tables:
            query = query.join(*list(unique(join_tables)))
        return query
    # }}}

    # {{{ Controller Interface
    def get_items(self, page=1, order_by=None, filters=None):
        """
        Fetch database for items matching.

        Args:
            page (int):
                which page will be sliced
                slice size is ``self.per_page``.
            order_by (str):
                a field name to order query by.
            filters (dict):
                a ``filter name``: ``value`` dict.

        Returns:
            tuple with:
                items, sliced by page*self.per_page
                total items without slice
        """
        start = (page-1)*self.per_page
        query = self.get_query()
        if order_by is not None:
            query = query.order_by(self._get_field(order_by))
        if filters is not None:
            query = self._filter(query, filters)
        return query.offset(start).limit(self.per_page), self.count(query)

    def get_item(self, pk):
        return self.get_query().get(pk)

    def create_item(self, form):
        item = self.new()
        return self.update_item(item, form)

    def update_item(self, item, form):
        form.populate_obj(item)
        return self.save(item)

    def delete_item(self, item):
        return self.delete(item)
    # }}}
