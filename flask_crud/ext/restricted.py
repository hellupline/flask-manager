from flask_login import current_user, login_required
from flask_crud import Group


class RestrictedGroup(Group):
    decorators = [login_required]

    def endpoints(self):
        user_roles = current_user.get_roles()
        endpoints = super().endpoints()
        return self._filter(endpoints, user_roles)

    def _filter(self, menu, user_roles):
        try:
            name, endpoint, children = menu
        except TypeError:
            return
        children = [self._filter(child, user_roles) for child in children]
        if endpoint.strip('.') in user_roles:
            return name, endpoint, list(filter(None.__ne__, children))


class RestrictedMixin:
    decorators = [login_required]

    def get_roles(self):
        user_roles = current_user.get_roles()
        roles = super().get_roles()
        return {
            key: list(set(values) & set(user_roles))
            for key, values in roles.items()
        }
