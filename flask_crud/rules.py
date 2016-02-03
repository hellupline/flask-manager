from functools import lru_cache

from flask import current_app
from jinja2 import Markup


@lru_cache()
def get_template(template_name):
    return current_app.jinja_env.get_or_select_template(template_name)


class Macro:
    template_name = None
    macro_name = None

    def __init__(self, template_name=None, macro_name=None, **kwargs):
        if template_name is not None:
            self.template_name = template_name
        if macro_name is not None:
            self.macro_name = macro_name
        self.kwargs = kwargs

    def _resolve(self):
        template = get_template(self.template_name)
        return getattr(template.module, self.macro_name)

    def __call__(self, obj, **kwargs):
        macro = self._resolve()
        opts = self.kwargs.copy()
        opts.update(kwargs)
        return macro(obj, **opts)


class Nested:
    """Nested([Rule(...), Rule(...)])"""

    def __init__(self, rules):
        self.rules = rules

    def __call__(self, obj, **kwargs):
        return Markup(''.join(rule(obj) for rule in self.rules))


class Container(Macro):
    """Container(Macro(...))()"""

    def __init__(self, child_rule, **kwargs):
        self.child_rule = child_rule
        super().__init__(**kwargs)

    def __call__(self, obj, **kwargs):
        def caller():
            return self.child_rule(obj)
        return super().__call__(obj, caller=caller, **kwargs)


# {{{ FieldMacros
class CellField(Macro):
    """Render a field in List."""
    template_name = 'crud/macros/table.html'
    macro_name = 'render_field'

    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super().__init__(**kwargs)

    def __call__(self, obj):
        try:
            value = getattr(obj, self.field_name)
        except AttributeError:
            value = obj[self.field_name]
        return super().__call__(obj, name=self.field_name, value=value)


class DataField(CellField):
    """Render a field in Read/Delete."""
    template_name = 'crud/macros/data.html'


class FormField(CellField):
    """Render a form field in Create/Update."""
    template_name = 'crud/macros/form.html'
# }}} FieldMacros


# {{{ RowContainers
class ColumnSet(Nested):
    """ColumnSet([name for name in model])(Model())"""
    field_class = CellField

    def __init__(self, columns):
        rules = [self.field_class(column) for column in columns]
        self.columns = columns
        super().__init__(rules=rules)


class DataFieldSet(ColumnSet):
    field_class = DataField


class FormFieldSet(ColumnSet):
    field_class = FormField


class DataFieldSetWithConfirm(ColumnSet):
    template_name = 'crud/macros/form.html'
    macro_name = 'render_form'
    field_class = DataField
# }}} RowContainers


# {{{ EyeCandy
class Text:
    def __init__(self, text, escape=True):
        self.text = text
        self.escape = escape

    def __call__(self, obj, **kwargs):
        if self.escape:
            return self.text
        return Markup(self.text)


class HTML(Text):
    def __init__(self, html):
        super().__init__(text=html, escape=False)


class Box(Container):
    """Box(Rule())()"""
    template_name = 'crud/macros/utils.html'
    macro_name = 'box'


class Foldable(Container):
    """Foldable(Rule())()"""
    template_name = 'crud/macros/utils.html'
    macro_name = 'foldable'


class Header(Macro):
    """Header('Title')()"""
    template_name = 'crud/macros/utils.html'
    macro_name = 'header'

    def __init__(self, html):
        super().__init__(text=html)


class SimpleForm(Macro):
    """SimpleForm()(Form())"""
    template_name = 'crud/macros/form.html'
    macro_name = 'simple_form_render'
# }}} EyeCandy
