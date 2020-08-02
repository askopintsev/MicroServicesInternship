from .views import views


def setup_routes(app):
    app.router.add_route("POST", "/login", views.login)
    app.router.add_route("POST", "/profile", views.profile)
    app.router.add_route("POST", "/register", views.register)
    app.router.add_route("POST", "/logout", views.logout)
    app.router.add_route("POST", "/refresh", views.refresh)
