from itertools import chain
import wtforms

from sqlalchemy import or_
from .base import Controller, Filter


class ColumnFilter(Filter):
    def __init__(self, column):
        self.column = column

    def filter(self, query, value):
        return query.filter(self.column == value)

    def get_values(self, query):
        values = query.with_entities(self.column)
        return set(chain.from_iterable(values))

    def get_form_field(self, key, query):
        choices = [
            (value, str(value).title())
            for value in self.get_values(query)
        ]
        return wtforms.SelectField(key.title(), choices=choices)


class JoinColumnFilter(ColumnFilter):
    def __init__(self, column, joined_table):
        self.joined_table = joined_table
        super().__init__(column=column)

    def join_query(self, query):
        return query.join(self.joined_table)

    def filter(self, query, value):
        return super().filter(self.join_query(query), value)

    def get_values(self, query):
        return super().get_values(self.join_query(query))


class SQLAlchemyController(Controller):
    def __init__(self, db_session=None, *args, **kwargs):
        if db_session is not None:
            self.db_session = db_session
        super().__init__(*args, **kwargs)

    def get_filter_form(self):
        class FilterForm(wtforms.Form):
            pass
        for key, filter_ in self.filters.items():
            setattr(FilterForm, key, filter_.get_form_field(key, self.get_query()))
        return FilterForm

    def get_filters(self, params):
        return [
            (self.filters[key], value)
            for key, value in params.items()
            if key in self.filters
        ]

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

    def _get_field(self, name):
        if name[0] == '-':
            return -getattr(self.model_class, name[1:])
        return getattr(self.model_class, name)

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
            query = query.order_by(self._get_field(order_by))
        if filters is not None:
            for filter_, value in self.get_filters(filters):
                query = filter_.filter(query, value)
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
