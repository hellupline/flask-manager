from collections import defaultdict

from flask_crud.utils import concat_urls, slugify
from flask_crud.views import LandingView, Roles
from flask_crud.tree import Tree
from flask_crud.components import List, Create, Read, Update, Delete


class Group(Tree):
    view_func = LandingView.as_view

    def __iter__(self):
        url = concat_urls(self.absolute_url)
        name = self._view_name()
        view = self.view_func(name, parent=self, view_name=name)
        yield url, name, view
        yield from super().__iter__()

    def endpoints(self):
        children = [item.endpoints() for item in self.items]
        endpoint = '.{}'.format(self._view_name())
        return self.name, endpoint, children

    def _view_name(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name, 'home'])


class ViewNode(Tree):
    def __init__(self, view_func, name=None, url=None):
        if name is None:
            name = view_func.__name__.title()
        self.view_func = view_func
        super().__init__(name=name, url=url)

    def __iter__(self):
        url = concat_urls(self.absolute_url)
        name = self.absolute_name
        yield url, name, self.view_func

    def endpoints(self):
        endpoint = '.{}'.format(self.absolute_name)
        return self.name, endpoint, ()


class Crud(Tree):
    components = (List, Read, Create, Update, Delete)
    decorators = ()
    rules = {}
    controller = None

    def __iter__(self):
        main_endpoint = '.{}'.format(self._main_component_name())
        for index, component in enumerate(self.components):
            url = concat_urls(self.absolute_url, component.url)
            name = self._component_name(component, index)
            view = component.as_view(
                name, crud=self, view_name=name,
                success_url=main_endpoint,
            )
            yield url, name, self._decorate_view(view)

    def endpoints(self):
        endpoint = '.{}'.format(self._main_component_name())
        return self.name, endpoint, ()

    def get_roles(self):
        roles = defaultdict(list)
        for index, component in enumerate(self.components):
            role = self._component_name(component, index)
            roles[component.role.name].append(role)
        return roles

    def _main_component_name(self):
        for index, component in enumerate(self.components):
            if component.role is Roles.list:
                return self._component_name(component, index)

    def _component_name(self, component, index):
        parts = [self.absolute_name, slugify(component.role.name)]
        if self.components.count(component) > 1:
            parts.append(str(index))
        return '-'.join(parts)

    def _decorate_view(self, view):
        for decorator in self.decorators:
            view = decorator(view)
        return view
