from collections import defaultdict
from cached_property import cached_property
import wtforms

from flask_manager import tree, components, utils


class FakeSelectMultipleField(wtforms.fields.SelectMultipleField):
    # prevent validation for value in choices
    def pre_validate(self, *args, **kwargs):
        return None


class Filter:
    def get_form_field(self, query):
        raise NotImplementedError

    def filter(self, value, items):
        raise NotImplementedError


# pylint: disable=abstract-method
class SearchFilter(Filter):
    def get_form_field(self):
        return wtforms.TextField()


class FieldFilter(Filter):
    def get_form_field(self):
        choices = [('', 'All'), *list(self.get_choices())]
        return wtforms.SelectField(choices=choices)

    def get_choices(self):
        raise NotImplementedError


class Controller(tree.Tree):
    components = (
        components.List,
        components.Create,
        components.Read,
        components.Update,
        components.Delete
    )
    decorators = ()
    display_rules = {}
    actions = {}
    filters = {}
    per_page = 100
    form_class = None

    def __init__(self, *args, **kwargs):
        attribute_keys = (
            'components', 'decorators', 'display_rules',
            'actions', 'filters', 'per_page', 'form_class'
        )
        for key in filter(kwargs.__contains__, attribute_keys):
            setattr(self, key, kwargs.pop(key))
        super().__init__(*args, **kwargs)

    def all_endpoints(self):
        for component in self.components:
            yield self._component_name(component)

    @cached_property
    def endpoint(self):
        return '.{}'.format(self._main_component_name())

    def get_nodes(self):
        endpoint = '.{}'.format(self._main_component_name())
        for component in self.components:
            yield self._get_view(component, endpoint)

    # {{{ Actions Interface
    def get_action_form(self):
        class ActionsForm(wtforms.Form):
            action = wtforms.fields.SelectField(choices=[
                (key, key.title()) for key in self.actions])
            ids = FakeSelectMultipleField('ids')
        return ActionsForm

    def execute_action(self, params):
        form = self.get_action_form()(params)
        if not form.validate():
            return False  # Raise Exception ?
        self.actions[form.action.data](self, form.ids.data)
    # }}}

    # {{{ Filter Interface
    def get_filter_form(self):
        class FilterForm(wtforms.Form):
            for key, filter_ in self.filters.items():
                vars()[key] = filter_.get_form_field()
                del key, filter_
        return FilterForm

    def get_filters(self, params):
        return [
            (self.filters[key], value)
            for key, value in params.items()
            if value and key in self.filters
        ]
    # }}}

    # {{{ Auth
    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            role = self._component_name(component)
            roles[component.role.name].append(role)
        return roles
    # }}}

    # {{{ Helpers
    def _main_component_name(self):
        # warn if no components.List Component, use a components.Create ?
        for component in self.components:
            if component.role is components.Roles.list:
                return self._component_name(component)

    def _component_name(self, component):
        return ':'.join([
            self.absolute_name,
            utils.slugify(component.role.name),
            component.__name__.lower(),
        ])

    def _decorate_view(self, view):
        for decorator in self.decorators:
            view = decorator(view)
        return view

    def _get_view(self, component, endpoint):
        url = utils.concat_urls(self.absolute_url, component.url)
        name = self._component_name(component)
        view = component.as_view(
            name, controller=self, view_name=name, success_url=endpoint)
        return url, name, self._decorate_view(view)
    # }}}

    # {{{ Controller Interface
    def get_items(self, page=1, order_by=None, filters=None):
        """Return a paginated list of columns."""
        raise NotImplementedError

    def get_item(self, pk):
        """Return a entry with PK."""
        raise NotImplementedError

    def create_item(self, form):
        """Create a new entry in the storage."""
        raise NotImplementedError

    def update_item(self, item, form):
        """Update a entry in storage."""
        raise NotImplementedError

    def delete_item(self, item):
        """Delete a new entry in storage."""
        raise NotImplementedError
    # }}}


class ViewNode(tree.Tree):
    def __init__(self, view_func, name=None, url=None):
        if name is None:
            name = view_func.__name__.title()
        self.view_func = view_func
        super().__init__(name=name, url=url)

    @cached_property
    def endpoint(self):
        return '.{}'.format(self.absolute_name)

    def get_nodes(self):
        url = utils.concat_urls(self.absolute_url)
        name = self.absolute_name
        yield url, name, self.view_func
