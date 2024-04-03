# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Adam Solchenberger <asolchenberger@gmail.com>
# Copyright (c) 2022 Jason Engman <jengman@testtech-solutions.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from typing import Any, Optional, Callable
import os, time
from sqlalchemy import desc
####################Different
from pycomm3 import tag
#####################
from .api import APIClass, PropertyError



from .database_conx import Connection, TAG_TYPES, UnknownConnectionError
from .database_tag import Tag
from .database import ConnectionsDb, DatabaseError
__all__ = ["DatabaseManager"]

CONNECTION_TYPES = {'local': Connection}
# try:
from .database_conx import LogixConnection
from .database_tag import LogixTag
CONNECTION_TYPES['logix'] =  LogixConnection
TAG_TYPES['logix'] =  LogixTag
from .database_conx import ModbusTCPConnection
from .database_tag import ModbusTcpTag
CONNECTION_TYPES['modbusTCP'] =  ModbusTCPConnection
TAG_TYPES['modbusTCP'] =  ModbusTcpTag
# except ImportError:
#     print('import error')

class DatabaseManager(APIClass):

    def __repr__(self) -> str:
        return "<class> DatabaseManager"
        
    def __init__(self) -> None:
        super().__init__()
        self._connection_types = CONNECTION_TYPES
        self._tag_types = TAG_TYPES
        self.properties += ['db_file', 'db_connection', 'connections', 'connection_types']
        self._db = None
        self._connections = {}
        self._db_file = None
        self.db_interface = ConnectionsDb()


    @property
    def connection_types(self) -> dict:
        return [key for key in self._connection_types]

    @property
    def db_file(self) -> str or None:
        return self._db_file

    @db_file.setter
    def db_file(self, path:str) -> None:
        self._db_file = path

    @property
    def db_connection(self) -> list:
        return self.query_for_connections()

    @property
    def connections(self):
        return self._connections

    def new_connection(self, params) -> "Connection":
        """
        pass params for the properties of the connection. This will include
        the connection type and extended properties for that type
        return the Connection() 
        """
        try:
            params['connection_type']
        except KeyError as e:
            raise PropertyError(f'Error creating connection, missing parameter: {e}')
        try:
            self.connections[params["id"]] = CONNECTION_TYPES[params['connection_type']](self, params)
            return self.connections[params["id"]]
        except KeyError as e:
            raise PropertyError(f'Error creating connection, unknown type: {e}')

    def parse_tagname(self, tagname: str) -> list[str, str]:
        return tagname.replace("[","").split("]")

    def load_db(self) -> bool:
        """
        load the settings db. return True if successful, else false
        if db is already loaded, this should close down the existing one first.
        this method only loads the db to the manager and gets the session
        ready. User is to call loading connections, tags, etc.
        """
        self.db_interface.db_file = self._db_file
        ##$#self.db_interface.open()
        session = self.db_interface.session
        orm = ConnectionsDb.models["connection-params-local"]
        conns = session.query(orm).all()
        for conn in conns:
            params = CONNECTION_TYPES[conn.connection_type].get_params_from_db(session, conn.id)
            conn_obj = self.new_connection(params)
            conn_obj.load_tags_from_db(session)
        return True

    def close_db(self) -> bool:
        """
        close the settings db. return None
        """
        self.db_interface.close()
    
    def save_connection(self, conn: "Connection") -> None:
        if self.db_interface.session:
            conn.save_to_db(self.db_interface.session)
        else:
            raise DatabaseError("Database has not been loaded")

    def get_connection_params(self, conn: "Connection",conx_id) -> None:
        if self.db_interface.session:
            return conn.get_params_from_db(self.db_interface.session,conx_id)

    def delete_connection(self, conn: "Connection",conx_id) -> None:
        try:
            del self.connections[conx_id]
            if self.db_interface.session:
                conn.delete_from_db(self.db_interface.session,conx_id)
        except KeyError as e:
            raise PropertyError(f'Connection does not exist: {e}')

    def delete_tag(self, tag: "Tag",tag_id,conx_id) -> None:
        print('Attemping to delete tag')
        if not self.connections[conx_id].polling:
            try:
                del self.connections[conx_id].tags[tag_id]
                if self.db_interface.session:
                    tag.delete_from_db(self.db_interface.session,tag_id)
            except KeyError as e:
                raise PropertyError(f'Tag does not exist: {e}')
        else:
            print('Tag Cannot be deleted while connection stil active')

    def save_tag(self, tag: "Tag") -> None:
        if self.db_interface.session:
            tag.save_to_db(self.db_interface.session)
        


            


