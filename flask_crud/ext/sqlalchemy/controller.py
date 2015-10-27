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

    def new(self):
        return self.model_class()

    def save(self, model):
        self.db_session.add(model)
        self.db_session.commit()
        return model

    def delete(self, model):
        self.db_session.delete(model)
        self.db_session.commit()

    def count(self, query):
        # sqlalchemy query.count() uses a generic subquery count, which
        # is slow, this one only replace the selected columns with a
        # COUNT(*)
        return query.statement.with_only_columns([func.count()]).scalar()

    def _get_field(self, name):
        if name[0] == '-':
            return -getattr(self.model_class, name[1:])
        return getattr(self.model_class, name)

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
            for filter_, value in self.get_filters(filters):
                query = filter_.filter(query, value)
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
