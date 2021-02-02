import logging
import sys

from ckan.common import config
from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled

from ..plugin import status, purge



class DatastoreCleanup(CkanCommand):
    """
    Usage::
        paster datastore_cleanup status
           - Displays count of active, deleted and total records in datastore
        paster datastore_cleanup purge
           - DESTRUCTIVE! Deletes all "deleted" datastore records.
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    # max_args = 1
    min_args = 0

    def __init__(self, name):
        super(DatastoreCleanup, self).__init__(name)

    def command(self):
        """
        """
        self._load_config()
        log = logging.getLogger(__name__)

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print DatastoreCleanup.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        from ckanext.datastore_cleanup import plugin as cleanup_plugin

        log = logging.getLogger(__name__)

        if cmd == 'status':
            self.status()
        elif cmd == 'purge':
            self.run()

    def status(self):
        return status()

    def purge(self):
        return purge()
