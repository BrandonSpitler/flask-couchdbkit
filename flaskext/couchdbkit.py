# -*- coding: utf-8 -*-
"""
    flaskext.couchdbkit
    ~~~~~~~~~~~~~~~~~~~

    Flask extension that provides integration with CouchDBKit.

    :copyright: (c) 2010 by Kridsada Thanabulpong.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement, absolute_import
import os
import couchdbkit
from flask import current_app
from restkit import SimplePool
from couchdbkit import Server
from couchdbkit.loaders import FileSystemDocsLoader


__all__ = ['CouchDBKit']


def _include_couchdbkit(obj):
    module = couchdbkit.schema
    for key in ('Document', 'DocumentSchema', 'Property', 'StringProperty',
                'IntegerProperty', 'DecimalProperty', 'BooleanProperty',
                'FloatProperty', 'DateTimeProperty', 'DateProperty',
                'TimeProperty', 'SchemaProperty', 'SchemaListProperty',
                'ListProperty', 'DictProperty', 'StringListProperty'):
        if not hasattr(obj, key):
            setattr(obj, key, getattr(module, key))


class CouchDBKit(object):
    """This class is used to control CouchDB integration to a Flask
    application.
    
    :param app: The application to bind this CouchDBKit instance into.
    """
    
    def __init__(self, app):
        app.config.setdefault('COUCHDB_SERVER', 'http://localhost:5984/')
        app.config.setdefault('COUCHDB_DATABASE', None)
        app.config.setdefault('COUCHDB_KEEPALIVE', 2)
        
        pool = SimplePool(keepalive=app.config.get('COUCHDB_KEEPALIVE'))
        server = Server(app.config.get('COUCHDB_SERVER'), pool_instance=pool)
        
        self.app = app
        self.server = server
        self.init_db()
        
        app.couchdbkit_manager = self
        
        _include_couchdbkit(self)
        self.Document.set_db(self.db)
    
    def init_db(self):
        """Initialize database object from the `COUCHDB_DATABASE`
        configuration variable. If the database does not already exists,
        it will be created.
        """
        dbname = self.app.config.get('COUCHDB_DATABASE')
        self.db = self.server.get_or_create_db(dbname)
        if hasattr(self, 'Document'):
            self.Document.set_db(self.db)
    
    def sync(self):
        """Sync the local views with CouchDB server."""
        design_path = os.path.join(self.app.root_path, '_design')
        loader = FileSystemDocsLoader(design_path)
        loader.sync(self.db)
