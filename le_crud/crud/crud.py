from collections import defaultdict
from .base import Group, concat_urls, slugify
from .components import List, Create, Read, Update, Delete, Permissions


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

    def get_permissions(self):
        permissions = defaultdict(list)
        for component in self.components:
            permission = component.permission
            if permission is Permissions.list:
                continue
            permissions[permission.name].append([
                component.name,
                self.component_absolute_name(component)
            ])
        return permissions

    def init_component(self, component_factory):
        kwargs = {
            'controller': self.controller,
            'display': self.display,
            'form_class': self.form_class,
            'permissions': self.get_permissions(),
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
            if component.permission is Permissions.list:
                continue
            yield self.name, self.component_absolute_name(component)

    def component_absolute_name(self, component):
        return '-'.join([self.absolute_name(), slugify(component.name)])
