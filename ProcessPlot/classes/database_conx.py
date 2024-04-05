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


from typing import Any, Optional
from .api import APIClass, PropertyError
from .database_tag import Tag
from .database import ConnectionsDb

__all__ = ["Connection", "TAG_TYPES", "UnknownConnectionError"]

TAG_TYPES = {'local': Tag}

class UnknownConnectionError(Exception):
    """
    raised when getting a connection that does not exist
    """


class Connection(APIClass):
    """
    The base connection class
    """

    def __repr__(self) -> str:
        return f"Connection: {self.id}"

    @property
    def id(self) -> str:
        return self._id

    @property
    def connection_type(self) -> str:
        return self._connection_type

    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, value: str) -> None:
        self._description = value


    @property
    def tags(self):
        return self._tags

    @classmethod
    def get_params_from_db(cls, session, id: str):
        params = None
        orm = ConnectionsDb.models["connection-params-local"]
        conn = session.query(orm).filter(orm.id == id).first()
        if conn:
            params = {
                'id': conn.id,
                'connection_type': conn.connection_type,
                'description': conn.description,
            }
        return params

    

    def __init__(self, manager: "database_manager",params: dict) -> None:
        super().__init__()
        self._tag_types = TAG_TYPES
        self.properties += ['id', 'connection_type', 'description', 'tags']
        try:
            params['id']
            params['connection_type']
        except KeyError as e:
            raise PropertyError(f"Missing expected property {e}")
        self._id = params.get('id')
        self._connection_type = "local" #base connection. Override this on exetended class' init to the correct type
        self._description = '' if 'description' not in params else params.get('description')
        self._tags = {}
        self._pollrate = 0.5 if 'pollrate' not in params else params.get('pollrate')
        self.base_orm = ConnectionsDb.models["connection-params-local"] # database object-relational-model
   
    def new_tag(self, params) -> "Tag":
        """
        pass params for the properties of the tag. This will include
        the connection type and extended properties for that type
        return the Tag() 
        """
        params['connection_id'] = self.id
        try:
            self.tags[params["id"]] = TAG_TYPES[self.connection_type](params)
            return self.tags[params["id"]]
        except KeyError as e:
            raise PropertyError(f'Error creating tag, unknown type: {e}')
        
    def save_to_db(self, session: "db_session") -> str:
        entry = session.query(self.base_orm).filter(self.base_orm.id == self.id).first()
        if entry == None:
            entry = self.base_orm()
        entry.id = self.id
        entry.connection_type = self.connection_type
        entry.description = self.description
        session.add(entry)
        session.commit()
        if not self._id == entry.id:
            self._id = entry.id # if db created this, the widget has a new id
        return entry.id
########################New
    def delete_from_db(self,session: "db_session",conx_id):
        if conx_id != None:
            session.query(self.base_orm).filter(self.base_orm.id == conx_id).delete()
            session.commit()
########################New
    def load_tags_from_db(self, session):
        orm = ConnectionsDb.models['tag-params-local']
        tags = session.query(orm).filter(orm.connection_id == self.id).all()
        for tag in tags:
            params = TAG_TYPES[self.connection_type].get_params_from_db(session, tag.id, self.id)
            self.new_tag(params)
########################New 
    def return_tag_parameters(self,*args):
        #default for local connection
        return ['id', 'connection_id', 'description','datatype','tag_type','value']
########################New 

    def connect_connection(self,conx_id,conx_params,tags):
        print('attemping connection')
        try:
            pass
            # self.con_man = ConxManager(self.process_link)
            # self.con_man.add_con(conx_params)
            # for t in tags:
            #     self.con_man.new_tag(conx_id, tags[t])
            # self.con_man.connect(conx_id)   #connection manager connect method attempt
            # return self.con_man.is_polling(conx_id) #Returns whether connection was successful
        except:
            print('failed')

    def disconnect_connection(self,conx_id,conx_params,tags):
        print('attemping disconnect')
        try:
            pass
            # if self.con_man is not bool:
            #     print('disconnecting', conx_id)
            #     self.con_man.disconnect(conx_id)
            #     status = self.con_man.is_polling(conx_id) #Returns whether disconnection was successful
            #     self.con_man = False
            #     return status
            # else:
            #     pass
        except:
            print('failed')


class LogixConnection(Connection):

    @property
    def pollrate(self) -> float:
        return self._pollrate
    @pollrate.setter
    def pollrate(self, value: float) -> None:
        self._pollrate = value

    @property
    def auto_connect(self) -> bool:
        return self._auto_connect
    @auto_connect.setter
    def auto_connect(self, value: bool) -> None:
        self._auto_connect = value

    @property
    def host(self) -> str:
        return self._host
    @host.setter
    def host(self, value: str) -> None:
        self._host = value

    @property
    def port(self) -> int:
        return self._port
    @port.setter
    def port(self, value: int) -> None:
        self._port = value

    @classmethod
    def get_params_from_db(cls, session, id: str):
        params = super().get_params_from_db(session, id)
        orm = ConnectionsDb.models["connection-params-logix"]
        conn = session.query(orm).filter(orm.id == id).first()
        if conn:
            params.update({
                'pollrate': conn.pollrate,
                'auto_connect': conn.auto_connect,
                'host': conn.host,
                'port': conn.port,
            })
        return params

    def __init__(self, manager: "database_manager",params: dict) -> None:
        super().__init__(manager, params)
        self.properties += ['pollrate', 'auto_connect', 'host', 'port']
        self._connection_type = "logix"
        self.orm = ConnectionsDb.models["connection-params-logix"]
        self._pollrate = params.get('pollrate') or 1.0
        self._auto_connect = params.get('auto_connect') or False
        self._port = params.get('port') or 44818
        try:
            self._host = params.get('host') or '127.0.0.1'
        except KeyError as e:
            raise PropertyError(f"Missing expected property {e}")

    def save_to_db(self, session: "db_session") -> str:
        id = super().save_to_db(session)
        entry = session.query(self.orm).filter(self.orm.id == id).first()
        if entry == None:
            entry = self.orm()
        entry.id = self.id
        entry.pollrate = self.pollrate
        entry.auto_connect = self.auto_connect
        entry.host = self.host
        entry.port = self.port
        session.add(entry)
        session.commit()
        return entry.id
########################New
    def return_tag_parameters(self,*args):
        return ['id', 'connection_id', 'description','datatype','tag_type','address','value']


class ModbusTCPConnection(Connection):
    @property
    def pollrate(self) -> float:
        return self._pollrate
    @pollrate.setter
    def pollrate(self, value: float) -> None:
        self._pollrate = value

    @property
    def auto_connect(self) -> bool:
        return self._auto_connect
    @auto_connect.setter
    def auto_connect(self, value: bool) -> None:
        self._auto_connect = value

    @property
    def host(self) -> str:
        return self._host
    @host.setter
    def host(self, value: str) -> None:
        self._host = value

    @property
    def port(self) -> int:
        return self._port
    @port.setter
    def port(self, value: int) -> None:
        self._port = value

    @property
    def station_id(self) -> int:
        return self._station_id
    @station_id.setter
    def station_id(self, value: int) -> None:
        self._station_id = value

    @property
    def status(self) -> bool:
        return self._status
    @status.setter
    def status(self, value: bool) -> None:
        self._status = value

    @classmethod
    def get_params_from_db(cls, session, id: str):
        params = super().get_params_from_db(session, id)
        orm = ConnectionsDb.models["connection-params-modbusTCP"]
        conn = session.query(orm).filter(orm.id == id).first()
        if conn:
            params.update({
                'pollrate': conn.pollrate,
                'auto_connect': conn.auto_connect,
                'host': conn.host,
                'port': conn.port,
                'station_id': conn.station_id,
                'status':conn.status,
            })
        return params

    def __init__(self, manager: "database_manager",params: dict) -> None:
        super().__init__(manager, params)
        self.properties += ['pollrate', 'auto_connect', 'host', 'port', 'station_id','status']
        self._connection_type = "modbusTCP"
        self.orm = ConnectionsDb.models["connection-params-modbusTCP"]
        self._pollrate = params.get('pollrate') or 1.0
        self._auto_connect = params.get('auto_connect') or False
        self._port = params.get('port') or 502
        self._host = params.get('host') or '127.0.0.1'
        self._station_id = params.get('station_id') or 1
        self._status = params.get('status') or False

    def save_to_db(self, session: "db_session") -> str:
        id = super().save_to_db(session)
        entry = session.query(self.orm).filter(self.orm.id == id).first()
        if entry == None:
            entry = self.orm()
        entry.id = self.id
        entry.pollrate = self.pollrate
        entry.auto_connect = self.auto_connect
        entry.host = self.host
        entry.port = self.port
        entry.station_id = self.station_id
        session.add(entry)
        session.commit()
        return entry.id

    def return_tag_parameters(self,*args):
        return ['id', 'connection_id', 'description','datatype','tag_type','address','word_swapped','byte_swapped','bit','value','func_type']
