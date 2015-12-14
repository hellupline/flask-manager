from collections import defaultdict
from functools import partial

from flask_crud.tree import Tree
from flask_crud.utils import concat_urls, slugify
from flask_crud.views import LandingView, Roles
from flask_crud.components import List, Create, Read, Update, Delete


class Group(Tree):
    def __init__(self, name, url=None, items=None,
                 view_func=LandingView.as_view):
        self.view_func = view_func
        super().__init__(name=name, url=url, items=items)

    def endpoints(self):
        children_endpoints = [
            endpoint for item in self.items for endpoint in item.endpoints()
        ]
        endpoint = '.{}'.format(self._view_endpoint())
        return [(self.name, endpoint, children_endpoints)]

    def iter_items(self):
        name = self._view_endpoint()
        view = self.view_func(
            name, full_name=name,
            tree=self.get_tree_endpoints()
        )
        yield concat_urls(self.absolute_url()), name, view
        yield from super().iter_items()

    def _view_endpoint(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name(), 'home'])


class ViewNode(Tree):
    def __init__(self, name, view_func, url=None):
        self.view_func = view_func
        super().__init__(name=name, url=url)

    def endpoints(self):
        return [(self.name, '.{}'.format(self.absolute_name()), ())]

    def iter_items(self):
        name = self.absolute_name()
        yield concat_urls(self.absolute_url()), name, self.view_func


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

    def endpoints(self):
        for component in self.components:
            if component.role is not Roles.list:
                continue
            endpoint = '.{}'.format(self._get_component_endpoint(component))
            yield self.name, endpoint, ()

    def iter_items(self):
        for component in self.components:
            url = concat_urls(self.absolute_url(), component.url)
            name = self._get_component_endpoint(component)
            func = partial(component.as_view, name, full_name=name)
            yield url, name, self.init_view(func)

    def init_view(self, view_factory):
        main_endpoint = self._get_component_endpoint(self.components[0])
        kwargs = {
            'controller': self.controller,
            'display': self.display,
            'roles': self.get_roles(),
            'tree': self.get_tree_endpoints(),
            'success_url': '.{}'.format(main_endpoint),
        }
        return view_factory(**kwargs)

    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            endpoint = '.{}'.format(self._get_component_endpoint(component))
            roles[component.role.name].append((component.name, endpoint))
        return roles

    def _get_component_endpoint(self, component):
        return '-'.join([self.absolute_name(), slugify(component.name)])
