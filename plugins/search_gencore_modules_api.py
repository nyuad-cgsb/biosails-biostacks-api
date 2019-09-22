# This is the class you derive to create a plugin
from airflow.plugins_manager import AirflowPlugin
import json

from add_packages_to_db import find_package_by_dep
from flask import Blueprint, jsonify, request
from flask_admin import BaseView, expose
from flask_admin.base import MenuLink

# Importing base classes that we need to derive
from airflow.hooks.base_hook import BaseHook
from airflow.models import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.executors.base_executor import BaseExecutor
from airflow.www.app import csrf

"""
This plugin serves up an API for searching gencore modules
"""

# Creating a flask blueprint to integrate the templates and static folder
# When trying to add css/js refs - use this
# <link rel="stylesheet" href="{{ url_for('search_plugin.static', filename='styles.css') }}" type="text/css">
SearchBlueprint = Blueprint(
    "search_plugin", __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/search_plugin')


class Search(BaseView):
    """This creates a flask admin blueprint view
    It shows up as http://localhost:8080/admin/searchpluginview/
    """

    @expose('/')
    def render_default_view(self):
        """
        This is never actually used, but airflow complains if a default view isn't rendered
        :return:
        """
        return self.render("search_plugin/search_plugin.html", content="Hello galaxy!")

    @expose('/health', methods=['GET'])
    @csrf.exempt
    def health(self):
        """Appears at : http://localhost:8080/admin/search/hello
        This is just an example of how to use the rest API in a flask blueprint"""
        return jsonify({'health': 'Status OK'})

    @expose('/search_modules', methods=['POST'])
    @csrf.exempt
    def search_modules(self):
        results = {}
        request_data = json.loads(request.data.decode('utf-8'))
        try:
            name = request_data.get('name')
            version = None
            if 'version' in request_data:
                version = request_data.get('version')
            modules = find_package_by_dep(name, version)
            results['modules'] = modules
        except Exception as e:
            results['error'] = str(e)
        return jsonify(results)


# This isn't directly used,
# but if you leave it out and try to generate a MenuLink it gives an error
v = Search(category="Search")

ml = MenuLink(
    category='Search',
    name='View Previous Uploads',
    url='/admin/airflow/graph?dag_id=add_gencore_modules_to_db')

ml = MenuLink(
    category='Search',
    name='View Previous Uploads',
    url='/admin/dagrun/?flt1_dag_id_equals=add_gencore_modules_to_db')


class AirflowSearchPlugin(AirflowPlugin):
    name = "search_plugin"
    operators = []
    sensors = []
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = [SearchBlueprint]
    menu_links = [ml]
