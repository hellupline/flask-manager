from flask_crud import rules

class JavaScript(rules.Macro):
    def __init__(self, macro_name='json_editor.javascript'):
        super().__init__(macro_name=macro_name)


class JsonField(rules.Macro):
    def __init__(self, field, schema_url=None, macro_name='json_editor.editor'):
        super().__init__(
            macro_name=macro_name, field=field, schema_url=schema_url)


class FormFieldSetWithJson(rules.FormFieldSet):
    def __init__(self, fields, json_fields, header=None,
                 field_class=rules.FormField):
        super().__init__(fields=fields, header=header, field_class=field_class)
        self.rules.extend(
            JsonField(field=field, schema_url=schema_url)
            for field, schema_url in json_fields.items()
        )
        self.rules.insert(0, JavaScript())
