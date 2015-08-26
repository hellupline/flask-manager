#!/usr/bin/env python
from flask import Flask

from le_crud import crud
import data


def build_crud():
    tag_crud = crud.Crud(
        name='Tag',
        controller=data.tag_controller,
        display=data.tag_display,
    )
    tagging = crud.Group(name='Tags', items=[data.tagkind_crud, tag_crud])
    le_crud_admin = crud.Group(name='Admin', items=[tagging])
    return le_crud_admin


def root():
    routes = [
        '<a href="{}">{}</a>'.format(rule, rule.endpoint)
        for rule in app.url_map.iter_rules()
    ]
    return '<html><body><pre>\n{}\n</pre></body></html>\n'.format(
        '\n'.join(sorted(routes))
    )


if __name__ == '__main__':
    app = Flask(__name__, template_folder='templates')
    app.add_url_rule('/sitemap', view_func=root)

    app.register_blueprint(build_crud().get_blueprint())

    # data.metadata.create_all()
    app.run(debug=True)
