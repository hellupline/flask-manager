from collections import defaultdict
from cached_property import cached_property

from flask_crud.utils import concat_urls, slugify
from flask_crud.views import LandingView, Roles
from flask_crud.tree import Tree
from flask_crud.components import List, Create, Read, Update, Delete


class ViewNode(Tree):
    def __init__(self, view_func, name=None, url=None):
        if name is None:
            name = view_func.__name__.title()
        self.view_func = view_func
        super().__init__(name=name, url=url)

    @cached_property
    def endpoint(self):
        return '.{}'.format(self.absolute_name)

    def get_nodes(self):
        url = concat_urls(self.absolute_url)
        name = self.absolute_name
        yield url, name, self.view_func


class Group(Tree):
    view_class = LandingView

    @cached_property
    def endpoint(self):
        return '.{}'.format(self._view_name())

    def get_nodes(self):
        yield from super().get_nodes()
        yield self._get_view()

    def _view_name(self):
        if self.is_root():
            return 'home'
        return self.absolute_name

    def _get_view(self):
        url = concat_urls(self.absolute_url)
        name = self._view_name()
        view = self.view_class.as_view(name, parent=self, view_name=name)
        return url, name, view


class Crud(Tree):
    components = (List, Create, Read, Update, Delete)
    decorators = ()
    rules = {}
    controller = None

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

    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            role = self._component_name(component)
            roles[component.role.name].append(role)
        return roles

    def _main_component_name(self):
        # warn if no List Component, use a Create ?
        for component in self.components:
            if component.role is Roles.list:
                return self._component_name(component)

    def _component_name(self, component):
        return ':'.join([
            self.absolute_name,
            slugify(component.role.name),
            component.__name__.lower(),
        ])

    def _decorate_view(self, view):
        for decorator in self.decorators:
            view = decorator(view)
        return view

    def _get_view(self, component, endpoint):
        url = concat_urls(self.absolute_url, component.url)
        name = self._component_name(component)
        view = component.as_view(
            name, crud=self, view_name=name, success_url=endpoint)
        return url, name, self._decorate_view(view)
