from jinja2 import Markup
from .display import get_render_ctx


class RuleMixin:
    def __call__(self, obj, extra_kwargs=None):
        raise NotImplementedError


# Simple Text
class Text(RuleMixin):
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


class Nested(RuleMixin):
    """Nested([DataField(...), DataField(...)])"""

    def __init__(self, rules):
        self.rules = rules

    def __iter__(self):
        return iter(self.rules)

    def __call__(self, obj, **kwargs):
        return Markup(''.join(rule(obj) for rule in self.rules))


class Macro(RuleMixin):
    macro_name = None
    kwargs = None

    def __init__(self, macro_name=None, **kwargs):
        if macro_name is not None:
            self.macro_name = macro_name
        self.kwargs = kwargs

    def _resolve(self):
        parts = self.macro_name.split('.')
        macro = get_render_ctx().resolve(parts[0])
        if not macro:
            raise ValueError('Cannot find macro {}.'.format(self.macro_name))
        for part in parts[1:]:
            macro = getattr(macro, part)
        return macro

    def __call__(self, obj, **kwargs):
        macro = self._resolve()
        if self.kwargs is not None:
            opts = self.kwargs.copy()
            opts.update(kwargs)
        else:
            opts = kwargs
        return macro(obj, **opts)


class Container(Macro):
    """Container(Macro('my_macro'))()"""

    def __init__(self, child_rule, **kwargs):
        self.child_rule = child_rule
        super().__init__(**kwargs)

    def __call__(self, obj, **kwargs):
        def caller():
            return get_render_ctx().call(self.child_rule, obj)
        return super().__call__(obj, caller=caller, **kwargs)


# Macros
class Header(Macro):
    """Header('Title')()"""
    macro_name = 'Utils.header'

    def __init__(self, text):
        super().__init__(text=text)


class Foldable(Container):
    macro_name = 'Utils.foldable'


class SimpleForm(Macro):
    """SimpleForm()(Form())"""
    macro_name = 'Form.simple_form_render'


# Crud Macros
class DataField(Macro):
    """Render a field in Read/Delete."""
    macro_name = 'Data.render_field'

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, obj):
        field_value = getattr(obj, self.field_name)
        return super().__call__(obj, name=self.field_name, value=field_value)


class CellField(DataField):
    """Render a field in List."""
    macro_name = 'Table.render_field'


class FormField(DataField):
    """Render a form field in Create/Update."""
    macro_name = 'Form.render_field'


# Containers
class DataFieldSet(Container):
    """DataFieldSet([name for name in model])(Model())"""
    macro_name = 'Data.render_data'
    field_class = DataField

    def __init__(self, columns, header=None):
        rules = [self.field_class(column) for column in columns]
        if header is not None:
            rules.insert(0, Header(header))
        self.columns = columns
        super().__init__(child_rule=Nested(rules))


class ColumnSet(DataFieldSet):
    macro_name = 'Table.render_row'
    field_class = CellField


class FormFieldSet(DataFieldSet):
    macro_name = 'Form.render_form'
    field_class = FormField
