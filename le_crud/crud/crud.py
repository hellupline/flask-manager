from collections import defaultdict
from .base import Group, concat_urls, slugify
from .components import List, Create, Read, Update, Delete, Roles


class Crud(Group):
    def __init__(self, controller, display, name, url,
                 form_class=None, components=None,
                 *args, **kwargs):
        if components is None:
            self.components = [List, Read, Create, Update, Delete]
        else:
            self.components = components
        self.controller = controller
        self.display = display
        self.form_class = form_class
        super().__init__(name=name, url=url, *args, **kwargs)

    def get_roles(self):
        roles = defaultdict(list)
        for component in self.components:
            role = component.role
            roles[role.name].append([
                component.name,
                '.{}'.format(self.component_absolute_name(component))
            ])
        return roles

    def init_component(self, component_factory):
        kwargs = {
            'controller': self.controller,
            'display': self.display,
            'form_class': self.form_class,
            'roles': self.get_roles(),
            'success_url': self.absolute_url(),
        }
        return component_factory(**kwargs)

    def iter_items(self):
        for component_factory in self.components:
            component = self.init_component(component_factory)
            name = self.component_absolute_name(component)
            for url in component.urls:
                url = concat_urls(self.absolute_url(), url)
                yield url, name, component.dispatch_request

    def iter_endpoints(self):
        for component in self.components:
            if component.role is Roles.list:
                continue
            yield self.name, self.component_absolute_name(component)

    def component_absolute_name(self, component):
        return '-'.join([self.absolute_name(), slugify(component.name)])
