#!/usr/bin/env python
from flask import Flask

import le_crud
import data


def build_crud():
    le_crud_admin = le_crud.Group(name='Admin', url='/admin/', items=[
        le_crud.Group(name='Tags', url='tagging/', items=[
            le_crud.Crud(
                name='Tag Kinds', url='tag-kinds/',
                controller=data.tagkind_controller,
                display=data.tagkind_display,
            ),
            le_crud.Crud(
                name='Tag', url='tag/',
                controller=data.tag_controller,
                display=data.tag_display,
            ),
        ]),
    ])
    return le_crud_admin


def root():
    routes = [
        '{} -> {}'.format(rule, rule.endpoint)
        for rule in app.url_map.iter_rules()
    ]
    return '<html><body><pre>\n{}\n</pre></body></html>\n'.format(
        '\n'.join(sorted(routes)).
        replace('<', '&lt;').
        replace('>', '&gt;')
    )


if __name__ == '__main__':
    app = Flask(__name__, template_folder='templates')
    app.add_url_rule('/sitemap', view_func=root)

    app.register_blueprint(build_crud().get_blueprint())

    # data.metadata.create_all()
    app.run(debug=True)
