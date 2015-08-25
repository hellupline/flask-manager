class Filter:
    def filter(self, query, value):
        raise NotImplementedError

    def get_form_field(self, key, query):
        raise NotImplementedError


class Controller:
    model_class = None
    form_class = None
    filters = None
    per_page = 10

    def __init__(self, model_class=None, form_class=None, filters=None,
                 per_page=None):
        if model_class is not None:
            self.model_class = model_class
        if form_class is not None:
            self.form_class = form_class
        if filters is not None:
            self.filters = filters
        if per_page is not None:
            self.per_page = per_page

    def get_filter_form(self):
        raise NotImplementedError

    def get_filters(self, params):
        raise NotImplementedError

    def get_items(self, page=1, order_by=None, filters=None):
        """
        Return a paginated list of columns.
        """
        raise NotImplementedError

    def get_item(self, pk):
        """Return a entry with PK."""
        raise NotImplementedError

    def create_item(self, form):
        """Create a new entry in the storage."""
        raise NotImplementedError

    def update_item(self, model, form):
        """Update a entry in storage."""
        raise NotImplementedError

    def delete_item(self, model):
        """Delete a new entry in storage."""
        raise NotImplementedError
