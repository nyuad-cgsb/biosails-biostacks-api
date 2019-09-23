# This is the class you derive to create a plugin
from airflow.plugins_manager import AirflowPlugin
import json

from add_packages_to_db import find_package_by_dep, JSONEncoder
from flask import Blueprint, jsonify, request
from flask_admin import BaseView, expose
from flask_admin.base import MenuLink
from airflow.www.app import csrf

"""
This plugin serves up an API for searching gencore modules
Call it in python like so:

```
import requests
import json
uri = 'http://localhost:8082/admin/search/search_modules'
body = {"name": "samtools"}
r = requests.post(uri, json=body) 
json_content = request.content
content = json.loads(json_content)
```
"""

# Creating a flask blueprint to integrate the templates and static folder
# When trying to add css/js refs - use this
# <link rel="stylesheet" href="{{ url_for('search_plugin.static', filename='styles.css') }}" type="text/css">
SearchBlueprint = Blueprint(
    "search_plugin", __name__,
    url_prefix='/search',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/search_plugin')


class Search(BaseView):
    """This creates a flask admin blueprint view
    It shows up as http://localhost:8080/admin/search/
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
        """Appears at : http://localhost:8080/admin/search/health
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
            for i, m in enumerate(modules):
                m = JSONEncoder().encode(m)
                m = json.loads(m)
                modules[i] = m
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
    admin_views = [v]
    flask_blueprints = [SearchBlueprint]
    menu_links = [ml]
