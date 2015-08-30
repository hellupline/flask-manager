import wtforms


class FakeSelectMultipleField(wtforms.fields.SelectMultipleField):
    # prevent validation for value in choices
    pre_validate = lambda *args: None


class Filter:
    def filter(self, query, value):
        raise NotImplementedError

    def get_form_field(self, key, query):
        raise NotImplementedError


class Controller:
    per_page = 10

    def __init__(self, model_class, form_class,
                 filters=None, actions=None, per_page=None):
        self.model_class = model_class
        self.form_class = form_class
        self.filters = filters
        self.actions = actions
        if per_page is not None:
            self.per_page = per_page

    def get_filter_form(self):
        raise NotImplementedError

    def get_filters(self, params):
        return [
            (self.filters[key], value)
            for key, value in params.items()
            if key in self.filters and value
        ]

    def get_action_form(self):
        if self.actions is not None:
            choices = [
                (key, key.title()) for key, action in self.actions.items()]
        else:
            choices = []
        class ActionsForm(wtforms.Form):
            ids = FakeSelectMultipleField('ids', coerce=int, choices=[])
            action = wtforms.fields.SelectField(choices=choices)
        return ActionsForm

    def execute_action(self, params):
        form = self.get_action_form()(params)
        if form.validate():
            self.actions[form.action.data](form.ids.data)

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
