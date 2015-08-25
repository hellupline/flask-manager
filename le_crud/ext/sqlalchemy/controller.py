import wtforms

from le_crud.controller import Controller


class SQLAlchemyController(Controller):
    def __init__(self, db_session=None, *args, **kwargs):
        if db_session is not None:
            self.db_session = db_session
        super().__init__(*args, **kwargs)

    def get_filter_form(self):
        class FilterForm(wtforms.Form):
            pass
        if self.filters is not None:
            for key, filter_ in self.filters.items():
                field = filter_.get_form_field(key, self.get_query())
                setattr(FilterForm, key, field)
        return FilterForm

    def get_filters(self, params):
        return [
            (self.filters[key], value)
            for key, value in params.items()
            if value and key in self.filters
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
