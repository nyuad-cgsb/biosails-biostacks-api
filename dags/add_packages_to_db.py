from binstar_client.utils import get_server_api, parse_specs
from pymongo import MongoClient
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pprint import pprint

client = MongoClient('mongodb://root:password@mongo:27017/')
db = client.gencore_modules
collection = db.modules

aserver_api = get_server_api()


def get_all_envs():
    """
    Get all envs for the nyuad-cgsb
    Don't get packages or projects
    :return:
    """
    packages = aserver_api.user_packages('nyuad-cgsb')
    envs = []
    for package in packages:
        if package['package_types'][0] == 'env':
            envs.append(package)
    return envs


def parse_env_dependencies(release_attrs):
    """Deps are written as package_name=version
    We want to split this to be more explicit with out versions
    """
    dependencies = []
    print('------------------------------------------')
    pprint(release_attrs)
    print('------------------------------------------')
    if 'dependencies' in release_attrs:
        for dep in release_attrs['dependencies']:
            dep_def = dep.split('=')
            if len(dep_def) > 1:
                dependencies.append({'name': dep_def[0], 'version': dep_def[1]})
            else:
                dependencies.append({'name': dep_def[0], 'version': 'latest'})
    return dependencies


def find_package_by_dep(name, version=None):
    """Filter packages by dependency names"""
    if name and version is not None:
        f = collection.aggregate([
            {
                "$unwind": "$dependencies"
            },
            {
                "$match": {
                    "$and":
                        [
                            {

                                "dependencies.name": name
                            },
                            {

                                "dependencies.version": version
                            }
                        ],
                }
            },
        ])
        f = list(f)
    else:
        f = collection.aggregate([
            {
                "$unwind": "$dependencies"
            },
            {
                "$match": {
                    "dependencies.name": name
                }
            },
        ])
        f = list(f)

    return f


def find_package(name, version=None):
    """
    Find the gencore modules by name or name and version
    :param name:
    :param version:
    :return:
    """
    if name and version is not None:
        p = collection.find_one({'$and': [{'name': name}, {'version': version}]})
    else:
        p = collection.find_one({'name': name})

    return p


def create_document(release_attr):
    """
    Prepare a document to insert into mongodb
    :param release_attr: attr returned by anaconda show api
    :return:
    """
    if 'name' in release_attr:
        dependencies = parse_env_dependencies(release_attr)
        name = release_attr['name']
        channels = release_attr['channels']
        document = {
            'name': name,
            'channels': channels,
            'dependencies': dependencies,
            'version': release_attr['version']
        }
        found = find_package(document['name'], document['version'])
        if not found:
            collection.insert_one(document)


def get_env_def(package, version):
    """
    Query the anaconda show api to get the environment data: name, version, deps
    :param package:
    :param version:
    :return:
    """
    release = aserver_api.release('nyuad-cgsb', package, version)
    release['distributions'][0]['attrs']['version'] = version
    return release['distributions'][0]['attrs']


def get_envs_and_add_to_db(ds, **kwargs):
    """
    Get all the gencore envs
    If they aren't in the database, put them there
    :return:
    """
    envs = get_all_envs()
    for env in envs:
        release_attr = get_env_def(env['name'], env['latest_version'])
        create_document(release_attr)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 9, 15),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': '@hourly',
}
dag = DAG('add_gencore_modules_to_db', catchup=False, default_args=default_args)

submit_qc_workflow_task = PythonOperator(
    dag=dag,
    task_id='add_gencore_modules_to_db',
    retries=1,
    retry_delay=100,
    provide_context=True,
    python_callable=get_envs_and_add_to_db,
)

