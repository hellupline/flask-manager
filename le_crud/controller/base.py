class Controller:
    search_fields = None
    per_page = 10

    def __init__(self,
                 model_class=None, form_class=None,
                 per_page=None, search_fields=None):
        if model_class is not None:
            self.model_class = model_class
        if form_class is not None:
            self.form_class = form_class
        if per_page is not None:
            self.per_page = per_page
        if search_fields is not None:
            self.search_fields = search_fields

    def get_items(self,
                  page=1, order_by=None, filters=None, search=None):
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