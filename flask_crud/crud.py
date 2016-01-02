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

    @cached_property
    def endpoint(self):
        return '.{}'.format(self._main_component_name())

    def get_nodes(self):
        endpoint = '.{}'.format(self._main_component_name())
        for index, component in enumerate(self.components):
            yield self._get_view(component, index, endpoint)

    def get_roles(self):
        roles = defaultdict(list)
        for index, component in enumerate(self.components):
            role = self._component_name(component, index)
            roles[component.role.name].append(role)
        return roles

    def _main_component_name(self):
        # warn if no List Component, use a Create ?
        for index, component in enumerate(self.components):
            if component.role is Roles.list:
                return self._component_name(component, index)

    def _component_name(self, component, index):
        return '-'.join([
            self.absolute_name,
            slugify(component.role.name),
            str(index)
        ])

    def _decorate_view(self, view):
        for decorator in self.decorators:
            view = decorator(view)
        return view

    def _get_view(self, component, index, endpoint):
        url = concat_urls(self.absolute_url, component.url)
        name = self._component_name(component, index)
        view = component.as_view(
            name, crud=self, view_name=name, success_url=endpoint)
        return url, name, self._decorate_view(view)
