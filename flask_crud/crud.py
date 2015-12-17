from collections import defaultdict

from flask_crud.tree import Tree
from flask_crud.utils import concat_urls, slugify
from flask_crud.views import LandingView, Roles
from flask_crud.components import List, Create, Read, Update, Delete


class Group(Tree):
    view_func = LandingView.as_view

    def __iter__(self):
        name = self._view_name()
        view = self.view_func(name, parent=self, view_name=name)
        yield concat_urls(self.absolute_url()), name, view
        yield from super().__iter__()

    def endpoints(self):
        children_endpoints = [
            endpoint
            for item in self.items
            for endpoint in item.endpoints()
        ]
        endpoint = '.{}'.format(self._view_name())
        return [(self.name, endpoint, children_endpoints)]

    def _view_name(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name(), 'home'])


class ViewNode(Tree):
    def __init__(self, name, view_func, url=None):
        self.view_func = view_func
        super().__init__(name=name, url=url)

    def __iter__(self):
        url = concat_urls(self.absolute_url())
        name = self.absolute_name()
        yield url, name, self.view_func

    def endpoints(self):
        return [(self.name, '.{}'.format(self.absolute_name()), ())]


class Crud(Tree):
    COMPONENTS = [List, Read, Create, Update, Delete]

    def __init__(self, controller, display, name, url=None, components=None):
        if components is None:
            self.components = self.COMPONENTS.copy()
        else:
            self.components = components
        self.controller = controller
        self.display = display
        super().__init__(name=name, url=url)

    def __iter__(self):
        main_endpoint = self._component_name(self._main_component())
        for component in self.components:
            url = concat_urls(self.absolute_url(), component.url)
            name = self._component_name(component)
            view = component.as_view(
                name, crud=self, view_name=name,
                success_url='.{}'.format(main_endpoint),
            )
            yield url, name, view

    def endpoints(self):
        for component in self.components:
            if component.role is Roles.list:
                endpoint = '.{}'.format(self._component_name(component))
                yield self.name, endpoint, ()

    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            role = (component.role.name, self._component_name(component))
            roles[component.role.name].append(role)
        return roles

    def _component_name(self, component):
        return '-'.join([self.absolute_name(), slugify(component.role.name)])

    def _main_component(self):
        for component in self.components:
            if component.role is Roles.list:
                return component
