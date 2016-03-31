from functools import partial
from math import ceil
from enum import Enum
import traceback

from flask import request, abort, url_for, flash, current_app
from werkzeug.datastructures import CombinedMultiDict

from flask_manager import views


# pylint: disable=abstract-method
class Component(views.View):
    role = None
    url = None

    def __init__(self, controller, *args, **kwargs):
        """
        Args:
            controller (Controller): ``controller`` parent.
        """
        self.controller = controller
        super().__init__(*args, **kwargs)

    def get_success_url(self, params=None, item=None):
        if params is None:
            return url_for(self.success_url)

        roles = self.controller.get_roles()
        if '_add_another' in params:
            return url_for(
                '.{}'.format(roles[Roles.create.name][0]))
        elif '_continue_editing' in params and item is not None:
            return url_for(
                '.{}'.format(roles[Roles.update.name][0]), pk=str(item.id))
        return url_for(self.success_url)

    # {{{ Permissions
    def is_allowed(self):
        roles = self.controller.get_roles()
        allowed = roles.get(self.role.name, ())
        return self.view_name in allowed
    # }}}

    # {{{ View
    def dispatch_request(self, *args, **kwargs):
        if not self.is_allowed():
            abort(401)
        return super().dispatch_request(*args, **kwargs)

    def context(self, external_ctx=None):
        ctx = {
            'display_rules': self.controller.display_rules.get(self.role.name),
            'tree': self.controller.endpoints_tree(),
            'roles': self.controller.get_roles(),
            'success_url': self.success_url,
        }
        if external_ctx is not None:
            ctx.update(external_ctx)
        return super().context(ctx)
    # }}}

    # {{{ Convenience
    def get_form_data(self):
        return CombinedMultiDict([request.form, request.files])

    def get_form(self, *args, **kwargs):
        return self.controller.form_class(*args, **kwargs)

    def get_item(self, pk):
        item = self.controller.get_item(pk)
        if item is None:
            abort(404)
        return item
    # }}}


class Roles(Enum):
    list = 1
    create = 2
    read = 3
    update = 4
    delete = 5


class List(Component):
    role = Roles.list
    url = ''
    template_name = ('crud/list.html', )

    def get(self):
        order_by = request.args.get('order_by')
        page = int(request.args.get('page', 1))

        filter_form = self.controller.get_filter_form()
        action_form = self.controller.get_action_form()
        url_generator = partial(
            url_for, request.url_rule.endpoint, **request.args)
        roles = self.controller.get_roles()
        has_roles = bool(
            roles.get('read') or
            roles.get('update') or
            roles.get('delete')
        )

        items, total = self.controller.get_items(
            page=page, order_by=order_by, filters=request.args)
        if self.controller.per_page == 0:
            pages = 0
        else:
            pages = ceil(total/self.controller.per_page)
        return {
            'forms': {
                'filter': {'show': bool(self.controller.filters),
                           'form': filter_form(request.args)},
                'action': {'show': bool(self.controller.actions),
                           'form': action_form()},
            },
            'has_roles': has_roles,
            'pagination': {
                'order_by': order_by,
                'page': page,
                'total': total,
                'pages': pages,
                'url_generator': url_generator,
            },
            'items': items,
        }

    def post(self):
        self.controller.execute_action(self.get_form_data())
        return self.get_success_url(), {}


class Create(Component):
    role = Roles.create
    url = 'create/'
    template_name = ('crud/form.html', 'crud/create.html')

    def get(self):
        form_data = self.get_form_data()
        form = self.get_form(form_data)
        return {'form': form}

    def post(self):
        form_data = self.get_form_data()
        form = self.get_form(form_data)
        success_url = None
        if form.validate():
            try:
                item = self.controller.create_item(form)
            except Exception as e:  # pylint: disable=broad-except
                current_app.logger.error(traceback.format_exc())
                flash(str(e))
            else:
                success_url = self.get_success_url(form_data, item)
        return success_url, {'form': form}


class Read(Component):
    role = Roles.read
    url = 'read/<pk>/'
    template_name = ('crud/read.html', )

    def get(self, pk):
        item = self.get_item(pk)
        return {'pk': pk, 'item': item}


class Update(Component):
    role = Roles.update
    url = 'update/<pk>/'
    template_name = ('crud/form.html', 'crud/update.html')

    def get(self, pk):
        item = self.get_item(pk)
        form = self.get_form(self.get_form_data(), obj=item)
        return {'pk': pk, 'item': item, 'form': form}

    def post(self, pk):
        form_data = self.get_form_data()
        item = self.get_item(pk)
        form = self.get_form(form_data, obj=item)
        success_url = None
        if form.validate():
            try:
                self.controller.update_item(item, form)
            except Exception as e:  # pylint: disable=broad-except
                current_app.logger.error(traceback.format_exc())
                flash(str(e))
            else:
                success_url = self.get_success_url(self.get_form_data(), item)
        return success_url, {'pk': pk, 'item': item, 'form': form}


class Delete(Component):
    role = Roles.delete
    url = 'delete/<pk>/'
    template_name = ('crud/delete.html', 'crud/read.html')

    def get(self, pk):
        item = self.get_item(pk)
        return {'pk': pk, 'item': item}

    def post(self, pk):
        item = self.get_item(pk)
        success_url = None
        try:
            self.controller.delete_item(item)
        except Exception as e:  # pylint: disable=broad-except
            current_app.logger.error(traceback.format_exc())
            flash(str(e))
        else:
            success_url = url_for(self.success_url)
        return success_url, {'pk': pk, 'item': item}
