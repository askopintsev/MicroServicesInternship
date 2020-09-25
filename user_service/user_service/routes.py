from .views import views


def setup_routes(app):
    app.router.add_route("POST", "/login", views.login)
    app.router.add_route("GET", "/profile", views.profile)
    app.router.add_route("POST", "/profile_update", views.profile_update)
    app.router.add_route("POST", "/register", views.register)
    app.router.add_route("POST", "/logout", views.logout)
    app.router.add_route("POST", "/refresh", views.refresh)
