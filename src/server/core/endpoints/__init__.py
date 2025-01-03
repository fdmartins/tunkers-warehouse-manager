from flask import Blueprint
from .mission import *
from .button import *
from .user import *
from .template import *
from .history import *
from .buffer import *
from .products import *
from .status404 import *

def create_endpoints(buffer_service):
    register_mission_routes()
    register_button_routes(buffer_service)
    register_user_routes()
    register_template_routes()
    register_history_routes()
    register_buffer_routes(buffer_service)
    register_products_routes()
    register_status404_routes()