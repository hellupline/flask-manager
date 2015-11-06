/*jslint browser:true */

var editor_field = (function() {
    var editor = null;

    function install(field_id, schema) {
        var field_widget = document.getElementById(field_id);
        var placeholder_widget = document.createElement('div');

        placeholder_widget.id = field_id + '_placeholder';
        field_widget.parentElement.insertBefore(placeholder_widget, field_widget);

        return build(placeholder_widget, schema, field_widget);
    }

    function build(placeholder_widget, schema, field_widget) {
        if (schema === undefined) {
            schema = {};
        }
        editor = new JSONEditor(placeholder_widget, {
            schema: schema,
            // -------
            // theme: 'bootstrap3',
            // iconlib: 'bootstrap3',
            // object_layout: 'grid',
            // show_errors: 'interaction',
            // -------
            upload: null,
            no_additional_properties: false,
            ajax: true,
            disable_edit_json: false,
            disable_collapse: false,
            disable_properties: false,
            disable_array_add: false,
            disable_array_reorder: false,
            disable_array_delete: false,
        });

        editor.on('ready', function() {
            try {
                editor.setValue(JSON.parse(field_widget.value));
            } catch(e) {
                console.log(e);
            }
        });

        editor.on('change', function() {
            field_widget.value = JSON.stringify(editor.getValue());
        });

        field_widget.onchange = function() {
            editor.setValue(JSON.parse(field_widget.value));
        };
    }

    return { editor: editor, install: install };
}());
