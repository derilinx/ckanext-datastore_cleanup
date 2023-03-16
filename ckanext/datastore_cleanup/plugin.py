import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan

from ckan import model
from ckanext.datastore import backend

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _auth(context):
    user = context.get('user')


def _resource_set(state='deleted'):
    resources = model.Session.query(model.Resource)\
               .filter_by(state=state).with_entities('id')
    return set(r[0] for r in resources)

@ckan.logic.side_effect_free
def status(context, data_dict):
    deleted = _resource_set()
    active = _resource_set('active')
    datastore_ids = set(backend.get_all_resources_ids_in_datastore())

    return {'active': len(active & datastore_ids),
            'deleted': len(deleted & datastore_ids),
            'datastore': len(datastore_ids)
            }


def purge(context, data_dict):
    deleted = _resource_set()
    datastore_ids = set(backend.get_all_resources_ids_in_datastore())

    # ok, getting dangerous here.
    # we can't actually call datastore_delete on a deleted resource
    # since datastore tries to get the resource through the packate. 

    backend.DatastoreBackend.register_backends()
    backend.DatastoreBackend.set_active_backend(ckan.common.config)
    _backend = backend.DatastoreBackend.get_active_backend()
    _backend.configure(ckan.common.config)


    for resource in (deleted & datastore_ids):
        resp = _backend.delete(context, {'resource_id': resource})
        #log.debug(resp)
        log.debug("Deleted %s from datastore" % resource)

    return {'deleted': len(deleted & datastore_ids)}


@tk.auth_disallow_anonymous_access
def is_sysadmin(context, data_dict):
    return {'success': context['auth_user_obj'] and context['auth_user_obj'].sysadmin}


class CleanupPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IClick)

    # IActions
    def get_actions(self):
        return {
            'datastore_cleanup_status': status,
            'datastore_cleanup_run': purge,
        }


    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'datastore_cleanup_status': is_sysadmin,
            'datastore_cleanup_run': is_sysadmin,
        }

    def get_commands(self):
        import click

        @click.group()
        def datastore_cleanup():
            pass

        @datastore_cleanup.command()
        def status():
            print(tk.get_action("datastore_cleanup_status")({}, {}))

        @datastore_cleanup.command()
        def purge():
            print(tk.get_action("datastore_cleanup_run")({}, {}))

        return [datastore_cleanup]


