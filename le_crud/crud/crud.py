from collections import defaultdict
from flask import Blueprint

from .base import Tree, View, concat_urls, slugify
from .components import List, Create, Read, Update, Delete, Roles


class LandingView(View):
    def __init__(self, tree, *args, **kwargs):
        self.tree = tree
        super().__init__(*args, **kwargs)

    def get(self):
        return {'tree': self.tree}


class Group(Tree):
    template_name = 'admin/landing.html'

    def __init__(self, name, url=None, items=None,
                 template_name=None, view_class=LandingView):
        if template_name is not None:
            self.template_name = template_name
        self.view_class = view_class
        super().__init__(name=name, url=url, items=items)

    def endpoints(self):
        endpoint = '.{}'.format(self._get_view_endpoint())
        return [(self.name, endpoint, [
            endpoint
            for item in self.items for endpoint in item.endpoints()
        ])]

    def iter_items(self):
        yield from super().iter_items()

        view = self.init_view(self.view_class)
        name = self._get_view_endpoint()
        url = concat_urls(self.absolute_url(), '')
        yield url, name, view.dispatch_request

    def init_view(self, view_factory):
        view_args = {
            'template_name': self.template_name,
            'tree': self.get_tree_endpoints(),
        }
        return view_factory(**view_args)

    def _get_view_endpoint(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name(), 'home'])

    def get_blueprint(self):
        bp = Blueprint(
            self.name.lower(), __name__,
            url_prefix=concat_urls(self.url),
            template_folder='../templates',  # XXX
        )

        # remove parent url
        absolute_url_len = len(concat_urls(self.absolute_url()))
        for url, name, view in self.iter_items():
            url = url[absolute_url_len:]
            bp.add_url_rule(url, name.lower(), view, methods=['GET', 'POST'])
        return bp


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
        for component_factory in self.components:
            component = self.init_component(component_factory)
            name = self._get_component_endpoint(component)
            for url in component.urls:
                url = concat_urls(self.absolute_url(), url)
                yield url, name, component.dispatch_request

    def init_component(self, component_factory):
        kwargs = {
            'controller': self.controller,
            'display': self.display,
            'roles': self.get_roles(),
            'success_url': self.absolute_url(),
            'tree': self.get_tree_endpoints(),
            'form_class': self.form_class,
        }
        return component_factory(**kwargs)

    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            role = component.role
            roles[role.name].append([
                component.name,
                '.{}'.format(self._get_component_endpoint(component))
            ])
        return roles

    def _get_component_endpoint(self, component):
        return '-'.join([self.absolute_name(), slugify(component.name)])
