from contextlib import contextmanager
import wtforms
from sqlalchemy import func

from flask_crud.controller import Controller


class SQLAlchemyController(Controller):
    def __init__(self, db_session=None, *args, **kwargs):
        if db_session is not None:
            self.db_session = db_session
        super().__init__(*args, **kwargs)

    def get_filter_form(self):
        if self.filters is not None:
            body = {
                key: filter_.get_form_field(key, self.get_query())
                for key, filter_ in self.filters.items()
            }
        else:
            body = {}
        return type('FilterForm', (wtforms.Form,), body)

    def get_query(self):
        return self.db_session.query(self.model_class)

    @contextmanager
    def transaction(self):
        try:
            yield self.db_session
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            self.db_session.close()
            raise

    def new(self):
        return self.model_class()

    def save(self, model):
        with self.transaction() as session:
            session.add(model)
        return model

    def delete(self, model):
        with self.transaction() as session:
            session.delete(model)

    def count(self, query):
        # sqlalchemy query.count() uses a generic subquery count, which
        # is slow, this one only replace the selected columns with a
        # COUNT(*)
        stmt = query.statement.with_only_columns([func.count()])
        return self.db_session.execute(stmt).scalar()

    def _get_field(self, name):
        if name[0] == '-':
            return -getattr(self.model_class, name[1:])
        return getattr(self.model_class, name)

    def _filter(self, query, filters):
        join_tables = set()
        for filter_, value in self.get_filters(filters):
            if filter_.join_tables is not None:
                join_tables |= set(filter_.join_tables)
            query = filter_.filter(query, value)
        if join_tables:
            query = query.join(*join_tables)
        return query

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
        start, end = (page-1)*self.per_page, (page)*self.per_page
        query = self.get_query()
        if order_by is not None:
            query = query.order_by(self._get_field(order_by))
        if filters is not None:
            query = self._filter(query, filters)
        return query.offset(start).limit(end), self.count(query)

    def get_item(self, pk):
        return self.get_query().get(pk)

    def create_item(self, form):
        model = self.new()
        return self.update_item(model, form)

    def update_item(self, model, form):
        form.populate_obj(model)
        return self.save(model)

    def delete_item(self, model):
        return self.delete(model)
