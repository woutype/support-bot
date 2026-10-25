from .user import user_router
from .admin import admin_router

routers = [
    user_router,
    admin_router,
]