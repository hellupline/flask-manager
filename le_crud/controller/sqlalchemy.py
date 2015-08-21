import operator
import functools

from .base import Controller


class SQLAlchemyController(Controller):
    def __init__(self, db_session=None, *args, **kwargs):
        if db_session is not None:
            self.db_session = db_session
        super().__init__(*args, **kwargs)

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

    def filter_by(self, filters, op=operator.and_):
        return functools.reduce(op, filters)

    def get_items(self,
                  page=1, order_by=None, filters=None, search=None):
        """
        Return a paginated list of columns.
        order_by will be used in a SQLAlchemy order_by.
        filters is a iterable with 2-items tuple of field, value.
        search is similar with filters, but use a OR condition instead.
        """
        start, end = (page-1)*self.per_page, (page)*self.per_page
        query = self.get_query()
        if None not in (search, self.search_fields):
            query = query.filter(self.filter_by([
                (field == search) for field in self.search_fields
            ], op=operator.or_))
        if filters is not None:
            query = query.filter(self.filter_by([
                (field == value) for field, value in filters
            ]))
        if order_by is not None:
            query = query.order_by(order_by)
        return query.offset(start).limit(end), query.count()

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
