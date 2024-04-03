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
from .database import ConnectionsDb
__all__ = ["Tag"]

import struct

class datatype():
    length = 1
    format_code = 'x'
    @classmethod
    def to_bytes(cls, val):
        return struct.pack(cls.format_code, val)
    
    @classmethod
    def from_bytes(cls, data):
        return struct.unpack(cls.format_code*(len(data) / cls.length))
    
    @classmethod
    def bit_read(cls, val, bit):
        return bool(val>>bit &0x01)

class dt_lreal(datatype):
    length = 8
    format_code = 'd'

class dt_ulint(datatype):
    length = 8
    format_code = 'Q'

class dt_lint(datatype):
    length = 8
    format_code = 'q'

class dt_real(datatype):
    length = 4
    format_code = 'f'

class dt_udint(datatype):
    length = 4
    format_code = 'I'

class dt_dint(datatype):
    length = 4
    format_code = 'i'

class dt_uint(datatype):
    length = 2
    format_code = 'H'

class dt_int(datatype):
    length = 2
    format_code = 'h'

class dt_usint(datatype):
    length = 1
    format_code = 'B'

class dt_sint(datatype):
    length = 2
    format_code = 'b'

datatypes = {
    'LREAL': dt_lreal,
    'ULINT': dt_ulint,
    'LINT': dt_lint,
    'REAL': dt_real,
    'UDINT': dt_udint,
    'DINT': dt_dint,
    'UINT': dt_uint,
    'INT': dt_int,
    'USINT': dt_usint,
    'SINT': dt_sint,
    'BOOL': None
}

class Tag(APIClass):
    """
    The base tag class
    """
    @property
    def id(self) -> str:
        return self._id

    @property
    def tag_type(self) -> int:
        return self._tag_type

    @property
    def connection_id(self) -> str:
        return self._connection_id

    @property
    def datatype(self) -> str:
        return self._datatype
    @datatype.setter
    def datatype(self, value: str) -> None:
        self._datatype = value

    @property
    def description(self) -> str:
        return self._description
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
    

    @property
    def value(self) -> Any:
        return self._value
    @value.setter
    def value(self, value: str) -> None:
        self._value = value
    
    @property
    def tagname(self) -> str:
        return f"[{self.connection_id}]{self.id}"


    @classmethod
    def get_params_from_db(cls, session, id: str, connection_id:str):
        params = None
        orm = ConnectionsDb.models["tag-params-local"]
        tag = session.query(orm).filter(orm.id == id).filter(orm.connection_id == connection_id).first()
        if tag:
            params = {
                'id': tag.id,
                'connection_id': tag.connection_id,
                'description': tag.description,
                #####################corrected next three lines###########################################################################################################
                'datatype': tag.datatype,
                'tag_type':tag.tag_type,
                'value': tag.value,
            }
        return params

    def __repr__(self) -> str:
        return f"Tag: [{self.connection_id}]{self.id}"
        
    def __init__(self, params: dict) -> None:
        super().__init__()
        self.properties += ['tagname', 'id', 'connection_id', 'datatype', 'description', 'value']       #Base tag properties 
        try:
            params['id']
            params['connection_id']
        except KeyError as e:
            raise PropertyError(f"Missing expected property {e}")
        self._id = params.get("id")
        self._tag_type = "local" #1=base tag. Override this on exetended class' init to the correct type
        self._datatype = params.get("datatype")
        self._description = params.get("description")
        self._value = params.get("value")
        self._connection_id = params["connection_id"]
        self.base_orm = ConnectionsDb.models['tag-params-local']
    
    def save_to_db(self, session: "db_session") -> int:
        entry = session.query(self.base_orm).filter(self.base_orm.id == self.id).filter(self.base_orm.connection_id == self.connection_id).first()
        if entry == None:
            entry = self.base_orm()
        entry.id=self.id
        entry.tag_type=self.tag_type
        entry.connection_id=self.connection_id
        entry.description=self.description
        entry.datatype = self.datatype
        entry.value = self.value
        session.add(entry)
        session.commit()
        if not self._id == entry.id:
            self._id = entry.id
        return entry.id

########################New
    def delete_from_db(self,session: "db_session",tag_id):
        if tag_id != None:
            session.query(self.base_orm).filter(self.base_orm.id == tag_id).delete()
            session.commit()


class LogixTag(Tag):
    ####################################
    @property
    def address(self) -> str:
        return self._address
    @address.setter
    def address(self, value: str) -> None:
        self._address = value
    ####################################

    @classmethod
    def get_params_from_db(cls, session, id: str, connection_id: str):
        params = super().get_params_from_db(session, id, connection_id)
        orm = ConnectionsDb.models["tag-params-logix"]
        tag = session.query(orm).filter(orm.id == id).filter(orm.connection_id == connection_id).first()
        if tag:
            params.update({
                'address': tag.address,
            })
        return params
    
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self.properties += ['address']
        self._tag_type = "logix"
        self.orm = ConnectionsDb.models['tag-params-logix']
        try:
            self._address = params['address']
        except KeyError as e:
            raise PropertyError(f"Missing expected property {e}")
    
    def save_to_db(self, session: "db_session") -> int:
        id = super().save_to_db(session)
        entry = session.query(self.orm).filter(self.orm.id == id).filter(self.orm.connection_id == self.connection_id).first()
        if entry == None:
            entry = self.orm()
        entry.id = self.id
        entry.address = self.address
        entry.connection_id = self.connection_id
        session.add(entry)
        session.commit()
        return entry.id
        

class ModbusTcpTag(Tag):
    ####################################New
    @property
    def address(self) -> int:
        return self._address
    @address.setter
    def address(self, value: int) -> None:
        self._address = value
    @property
    def datatype(self) -> str:
        return self._datatype
    @datatype.setter
    def datatype(self, value: str) -> None:
        self._datatype = value
    @property
    def word_swapped(self) -> bool:
        return self._word_swapped
    @word_swapped.setter
    def word_swapped(self, value: bool) -> None:
        self._word_swapped = value
    @property
    def byte_swapped(self) -> bool:
        return self._byte_swapped
    @byte_swapped.setter
    def byte_swapped(self, value: bool) -> None:
        self._byte_swapped = value
    @property
    def bit(self) -> int:
        return self._bit
    @bit.setter
    def bit(self, value: int) -> None:
        self._bit = value
    @property
    def func_type(self) -> int:
        return self._func_type
    @func_type.setter
    def func_type(self, value: int) -> None:
        self._func_type = value
    ####################################New

    @classmethod
    def get_params_from_db(cls, session, id: str, connection_id: str):
        params = super().get_params_from_db(session, id, connection_id)
        orm = ConnectionsDb.models["tag-params-modbus"]
        tag = session.query(orm).filter(orm.id == id).filter(orm.connection_id == connection_id).first()
        if tag:
            params.update({
                'address': tag.address,
                'word_swapped': tag.word_swapped,
                'byte_swapped': tag.byte_swapped,
                'bit': tag.bit,
                'func_type':tag.func_type,
            })
        orm2 = ConnectionsDb.models["tag-params-local"]
        tag = session.query(orm2).filter(orm2.id == id).filter(orm2.connection_id == connection_id).first()
        if tag:
            params.update({
                'datatype':tag.datatype 
            })
        return params
    
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self.properties += ['address','word_swapped','byte_swapped','bit','datatype','func_type']
        self._tag_type = "modbus"
        self.orm = ConnectionsDb.models['tag-params-modbus']
        self._datatype = params.get('datatype') or 'REAL'
        self._word_swapped = params.get('word_swapped') or False
        self._byte_swapped = params.get('byte_swapped') or False
        self._bit = params.get('bit') or 1
        self._dt = params.get('datatype') or 'INT'
        self._func_type = params.get('func_type') or 4
        try:
            self._address = params['address']
        except KeyError as e:
            raise PropertyError(f"Missing expected property {e}")
    
    def save_to_db(self, session: "db_session") -> int:
        id = super().save_to_db(session)
        entry = session.query(self.orm).filter(self.orm.id == id).filter(self.orm.connection_id == self.connection_id).first()
        if entry == None:
            entry = self.orm()
        entry.id = self.id
        entry.address = self.address
        entry.connection_id = self.connection_id
        entry.word_swapped = self.word_swapped
        entry.byte_swapped = self.byte_swapped
        entry.bit = self.bit
        entry.func_type = self.func_type
        session.add(entry)
        session.commit()
        return entry.id