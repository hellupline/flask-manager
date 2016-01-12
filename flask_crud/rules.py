from jinja2 import Markup
from flask_crud.utils import get_render_ctx


class Macro:
    macro_name = None

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
            return get_render_ctx().call(self.child_rule, obj)
        return super().__call__(obj, caller=caller, **kwargs)


# {{{ FieldMacros
class CellField(Macro):
    """Render a field in List."""
    macro_name = 'Table.render_field'

    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super().__init__(**kwargs)

    def __call__(self, obj):
        value = getattr(obj, self.field_name)
        return super().__call__(obj, name=self.field_name, value=value)


class DataField(CellField):
    """Render a field in Read/Delete."""
    macro_name = 'Data.render_field'


class FormField(CellField):
    """Render a form field in Create/Update."""
    macro_name = 'Form.render_field'
# }}} FieldMacros


# {{{ RowContainers
class ColumnSet(Container):
    macro_name = 'Table.render_row'
    field_class = CellField

    def __init__(self, columns):
        rules = [self.field_class(column) for column in columns]
        self.columns = columns
        super().__init__(child_rule=Nested(rules))


class DataFieldSet(ColumnSet):
    """DataFieldSet([name for name in model])(Model())"""
    macro_name = 'Data.render_data'
    field_class = DataField


class FormFieldSet(ColumnSet):
    macro_name = 'Form.render_form'
    field_class = FormField

    def __init__(self, columns):
        super().__init__(columns=columns)
        self.child_rule.rules.append(FormButtons())


class DataFieldSetWithConfirm(ColumnSet):
    macro_name = 'Form.render_form'
    field_class = DataField

    def __init__(self, columns):
        super().__init__(columns=columns)
        self.child_rule.rules.append(
            FormButtons(submit_text='Confirm', type='danger'))
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


class Header(Macro):
    """Header('Title')()"""
    macro_name = 'Utils.header'

    def __init__(self, text, **kwargs):
        super().__init__(text=text, **kwargs)


class Box(Container):
    """Box(Rule())()"""
    macro_name = 'Utils.box'


class Foldable(Container):
    """Foldable(Rule())()"""
    macro_name = 'Utils.foldable'


class SimpleForm(Macro):
    """SimpleForm()(Form())"""
    macro_name = 'Form.simple_form_render'


class FormButtons(Macro):
    """FormButtons()(Form())"""
    macro_name = 'Form.buttons'
# }}} EyeCandy
