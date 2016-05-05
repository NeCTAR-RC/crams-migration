from rcportal_migration.settings import NECTAR_DB

class RcallocationRouter(object):
    """
    A router to control all database operations on models in the
    rcallocation application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read rcallocation models go to NECTAR_DB.
        """
        if model._meta.app_label == 'rcallocation':
            return NECTAR_DB
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write rcallocation models go to NECTAR_DB.
        """
        if model._meta.app_label == 'rcallocation':
            return NECTAR_DB
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the rcallocation app is involved.
        """
        if obj1._meta.app_label == 'rcallocation' or \
           obj2._meta.app_label == 'rcallocation':
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the crams app only appears in the NECTAR_DB
        database.
        """
        if app_label == 'rcallocation':
            return db == NECTAR_DB
        return None
