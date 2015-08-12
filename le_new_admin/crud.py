from flask import Blueprint, request, render_template, redirect, abort

from .controller import SQLAlchemyController
from .display import SQLAlchemyDisplay


"""
LIST:
    get:
        receive page
        return a context ( with items )
    post:
        execute action
        return a success and a context ( for errors )

CREATE:
    get:
        return a context ( with form )
    post:
        save obj
        return a success and a context ( for errors )
READ:
    get:
        return a context ( with item )
UPDATE:
    get:
        receive a pk
        fetch obj to form
        return a context ( with form )
    post:
        receive a pk
        save obj
        return a success and a context ( for errors )
DELETE:
    get:
        receive a pk
        return a context ( with item )
    post:
        receive a pk
        delete obj
        return a success and a context ( for errors )
"""


def concat_urls(url_a, url_b):
    return '/'.join([url_a.rstrip('/'), url_b.lstrip('/')])


def slugify(value):
    return value.lower().replace(' ', '_')


class Component:
    display = None
    form_class = None

    def __init__(self, controller, display, success_url,
                 form_class=None,
                 urls=None, name=None, template_name=None):
        self.controller = controller  # from crud
        self.display = display  # from crud
        self.success_url = success_url  # from crud

        if form_class is not None:
            # overwrite display's form_class
            self.form_class = form_class
        if urls is not None:
            self.urls = urls
        if name is not None:
            self.name = name
        if template_name is not None:
            self.template_name = template_name

    # Template
    def get_template_name(self):
        return self.template_name

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)

    # Form
    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class
        return self.display.form_class

    def get_form(self, *args, **kwargs):
        return self.get_form_class()(*args, **kwargs)

    def get_item(self, pk):
        item = self.controller.get_item(pk)
        if item is None:
            abort(404)
        return item

    # Context
    def get_context(self, extra=None):
        ctx = {
            'display': self.display
        }
        if extra is not None:
            ctx.update(extra)
        return ctx

    # Views
    def get(self, *args, **kwargs):
        raise NotImplementedError

    def post(self, *args, **kwargs):
        raise NotImplementedError

    def dispatch_request(self, **kwargs):
        if request.method == 'POST':
            success, do_redirect, context = self.post(**kwargs)
            if success and do_redirect:
                return redirect(self.success_url)
        elif request.method == 'GET':
            context = self.get(**kwargs)
        return self.render_template(context)


class Read(Component):
    urls = ['read/<int:pk>/']
    name = 'Read'
    template_name = 'admin/read.html'

    def get(self, pk):
        item = self.get_item(pk)
        return self.get_context({'item': item})

    def post(self, pk):
        raise Exception('Method Not Allowed')


class Create(Component):
    urls = ['create/']
    name = 'Create'
    template_name = 'admin/create.html'

    def get(self):
        form = self.get_form()
        return self.get_context({'form': form})

    def post(self):
        form = self.get_form(request.form)

        success = form.validate()
        if success:
            self.controller.create_item(form)
        # else:
            # flash errors or let form do
        return success, True, self.get_context({'form': form})


class Update(Component):
    urls = ['update/<int:pk>/']
    name = 'Update'
    template_name = 'admin/update.html'

    def get(self, pk):
        item = self.get_item(pk)
        form = self.get_form(obj=item)
        return self.get_context({'item': item, 'form': form})

    def post(self, pk):
        item = self.get_item(pk)
        form = self.get_form(request.form)
        success = form.validate()
        if success:
            self.controller.update_item(item, form)
        # else:
            # flash errors or let form do
        return success, True, self.get_context({'item': item, 'form': form})


class Delete(Component):
    urls = ['delete/<int:pk>/']
    name = 'Delete'
    template_name = 'admin/delete.html'

    def get(self, pk):
        item = self.get_item(pk)
        return self.get_context({'item': item})

    def post(self, pk):
        item = self.get_item(pk)
        self.controller.delete_item(item)
        return True, True, self.get_context()


class List(Component):
    urls = ['list/', 'list/<int:page>/', '']
    name = 'List'
    template_name = 'admin/list.html'

    def get(self, page=1):
        items = self.controller.get_items(page)
        return self.get_context({'items': items})

    def post(self):
        action = request.form['action']
        return self.get_context({'action': action})


class Group:
    items = None
    parent = None

    def __init__(self, name, url, items=None):
        self.name = name
        self.url = url
        self.register_items(items)

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.absolute_name()
        )

    # Register
    def register_item(self, item):
        item.register_parent(self)
        self.items.append(item)

    def register_parent(self, parent):
        if parent is not None:
            self.parent = parent

    def register_items(self, items):
        if items is None:
            return
        if self.items is None:
            self.items = []
        for item in items:
            item.register_parent(self)
        self.items.extend(item for item in items)

    # Tree
    def is_root(self):
        return self.parent is None

    def absolute_url(self):
        if self.is_root():
            return self.url
        return concat_urls(self.parent.absolute_url(), self.url)

    def absolute_name(self):
        if self.is_root() or self.parent.is_root():
            return self.name
        return '-'.join([self.parent.absolute_name(), slugify(self.name)])

    def iter_items(self):
        for item in self.items:
            yield from item.iter_items()
        yield self.landing_view()

    def iter_endpoints(self):
        yield (self.name, self._endpoint_name()), [
            list(item.iter_endpoints()) for item in self.items
        ]

    def get_blueprint(self):
        bp = Blueprint(self.name.lower(), __name__)
        for url, name, view in self.iter_items():
            bp.add_url_rule(url, name.lower(), view, methods=['GET', 'POST'])
        return bp

    # View
    def landing_view(self):
        name = self._endpoint_name()
        url = concat_urls(self.absolute_url(), '')
        return url, name, self.dispatch_request

    def _endpoint_name(self):
        if self.is_root():
            return 'home'
        return '-'.join([self.absolute_name(), 'home'])

    def dispatch_request(self):
        from pprint import pformat
        context = {
            'items': list(self.iter_endpoints())
        }
        f = pformat(context)
        return '<html><body><pre>\n{}\n</pre></body></html>\n'.format(f)


class Crud(Group):
    components = None
    controller = None
    display = None
    form_class = None

    def __init__(self,
                 controller, display=None, form_class=None,
                 components=None, *args, **kwargs):
        if display is not None:
            self.display = display
        if form_class is not None:
            self.form_class = form_class
        if components is not None:
            self.components = components
        else:
            self.components = [List, Read, Create, Update, Delete]
        self.controller = controller
        super().__init__(*args, **kwargs)

    def init_component(self, component_factory):
        kwargs = {
            'controller': self.controller,
            'success_url': self.absolute_url(),
            'display': self.display,
            'form_class': self.form_class,
        }
        return component_factory(**kwargs)

    def component_name(self, component):
        return '-'.join(
            [self.absolute_name(), component.name]
        ).lower().replace(' ', '_')

    def iter_items(self):
        for component_factory in self.components:
            component = self.init_component(component_factory)
            name = self.component_name(component)
            for url in component.urls:
                url = concat_urls(self.absolute_url(), url)
                yield url, name, component.dispatch_request

    def iter_endpoints(self):
        for component_factory in self.components:
            if not issubclass(component_factory, List):
                continue
            yield self.name, self.component_name(component_factory)


class SQLAlchemyCrud(Crud):
    def __init__(self, model, *args, **kwargs):
        controller = SQLAlchemyController(model)
        display = SQLAlchemyDisplay(model)
        super().__init__(
            *args, controller=controller, display=display, **kwargs)
