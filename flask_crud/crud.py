from collections import defaultdict
from functools import partial

from flask_crud.base import TemplateView, Tree, Roles, concat_urls, slugify
from flask_crud.components import List, Create, Read, Update, Delete


class LandingView(TemplateView):
    template_name = 'admin/landing.html'

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree
        super().__init__(*args, **kwargs)

    def get(self):
        return {'tree': self.tree}


class Group(Tree):
    def __init__(self, name, url=None, items=None, view_class=LandingView):
        self.view_class = view_class
        super().__init__(name=name, url=url, items=items)

    def endpoints(self):
        endpoint = '.{}'.format(self._get_view_endpoint())
        return [(self.name, endpoint, [
            endpoint for item in self.items for endpoint in item.endpoints()
        ])]

    def iter_items(self):
        yield from super().iter_items()
        name = self._get_view_endpoint()
        view = self.init_view(partial(self.view_class.as_view, name))
        yield concat_urls(self.absolute_url(), ''), name, view

    def init_view(self, view_factory):
        return view_factory(tree=self.get_tree_endpoints())

    def _get_view_endpoint(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name(), 'home'])


class Crud(Tree):
    COMPONENTS = [List, Read, Create, Update, Delete]

    def __init__(self, controller, display, name, url=None,
                 form_class=None, components=None):
        if components is None:
            self.components = self.COMPONENTS.copy()
        else:
            self.components = components
        self.controller = controller
        self.display = display
        self.form_class = form_class
        super().__init__(name=name, url=url, items=None)

    def endpoints(self):
        for component in self.components:
            if component.role is not Roles.list:
                continue
            endpoint = '.{}'.format(self._get_component_endpoint(component))
            yield self.name, endpoint, ()

    def iter_items(self):
        for component in self.components:
            name = self._get_component_endpoint(component)
            view = self.init_view(partial(component.as_view, name))
            for url in component.urls:
                yield concat_urls(self.absolute_url(), url), name, view

    def init_view(self, view_factory):
        endpoint = self._get_component_endpoint(self.components[0])
        kwargs = {
            'controller': self.controller,
            'display': self.display,
            'roles': self.get_roles(),
            'tree': self.get_tree_endpoints(),
            'success_url': '.{}'.format(endpoint),
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
