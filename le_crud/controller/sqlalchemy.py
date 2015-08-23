from sqlalchemy import and_, or_
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

    def get_items(self,
                  page=1, order_by=None, filters=None, search=None):
        """
        Fetch database for items matching.

        Args:
            page (int):
                which page will be sliced
                slice size is ``self.per_page``
            order_by (InstrumentedAttribute):
                a field used to order query
            filters (Iterable):
                a iterable with sqlalchemy Expressions
                will be merged with sqlalchemy.and_
            search (Iterable):
                a iterable with sqlalchemy Expressions
                will be merged with sqlalchemy.or_

        Returns:
            tuple with:
                items, sliced by page*self.per_page
                total items without slice
        """
        start, end = (page-1)*self.per_page, (page)*self.per_page
        query = self.get_query()
        if order_by is not None:
            query = query.order_by(order_by)
        if filters is not None:
            query = query.filter(and_(*filters))
        if search is not None:
            query = query.filter(or_(*search))
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
