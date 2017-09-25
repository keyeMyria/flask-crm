import random
import string
from enum import Enum
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm.collections import  InstrumentedList
from sqlalchemy.sql.sqltypes import TIMESTAMP
from crm.admin.mixins import AdminLinksMixin


db = SQLAlchemy()
db.session.autocommit = True


class RootModel(object):
    pass


class BaseModel(AdminLinksMixin):
    """
    Base Class for all models
    """

    id = db.Column(
        db.String(5),
        primary_key=True
    )

    created_at = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    @property
    def uid(self):
        """
        :return: Unique ID for that record
        :rtype: str
        """
        if self.id:
            return self.id
        while True:
            uid = ''.join(
                random.sample(
                    string.ascii_lowercase + string.digits,
                    5
                )
            )

            if not self.query.filter_by(id=uid).count():
                return uid

    @property
    def short_description(self):
        return "\n".join(
            getattr(self, 'description', '').splitlines()[:3]
        )

    @property
    def short_content(self):
        return "\n".join(
            getattr(self, 'content', '').splitlines()[:3]
        )

    @property
    def created_at_short(self):
        return self.created_at.strftime("%Y-%m-%d")

    @property
    def updated_at_short(self):
        return self.updated_at.strftime("%Y-%m-%d")

    @property
    def datetime_fields(self):
        """
        List ALL datetime fields
        Reason this is important, is that when serializing object into JSON
        we use ujson which serializes dates into epoch
        then when we need to load data from JSON files again, we need to be
        aware of datetime/date fields so that we can deserialize epoch fields
        
        :return: datetime/date fields
        :rtype: list
        """
        dt_fields = []
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime) or isinstance(value, date):
                dt_fields.append(c.name)
        return dt_fields

    def as_dict(self, resolve_refs=True):
        """
        If we are serializing object, we serialize all fields then we go into
        F.K fields and Back reference fields and serialize objects there (one level)
        i.e we don't care about their F.Ks nor Back reference fields
    
        :param resolve_refs: Resolve F.K & Back reference fields into dicts or not
        :type: resolve_refs: bool
        :return: Model object as dict
        :rtype: dict
        """
        data = {}

        for column in inspect(self.__class__).attrs.keys():
            value = getattr(self, column)
            data[column] = value
            # Foreign key -- resolve it (only 1 level)
            if isinstance(value, db.Model):
                data[column] = value.as_dict(resolve_refs=False)
            # Back references -- resolve them (only 1 level)
            elif isinstance(value, InstrumentedList):
                data[column] = [] # Leave empty if resolve_refs == False
                if resolve_refs:
                    for item in value:
                        data[column].append(item.as_dict(resolve_refs=False))
            # Enums are represented as {'name': 'PENDING', 'value': 0}
            # Enum -- We care only about name field.
            elif isinstance(value, Enum):
                data[column] = value.name

        data['model'] = self.__class__.__name__
        return data

    @staticmethod
    def from_dict(data):
        """
        Passed is a dictionary that represents a model object
        It can contain other dicts (each one is a F.K to another model object)
        It also can contain lists of dicts representing list of another model objects
        that is connected to our model object with back reference relation
        Basically we need to return list of models representing all data in the passed 
        dictionary.
        
        :param data: Dictionary of model object we want to deserialize into many model objects
        :type data: dict
        :return: list of model objects
        :rtype: list
        """
        all_models = {}

        for model in BaseModel.__subclasses__():
            all_models[model.__name__] = model

        def deserialize(data):
            model_name = data.pop('model')
            model = all_models[model_name]()

            not_serialized = []

            for field, value in data.items():
                # Make datetime from epoch -- If field type is TIMESTAMP
                # Remember that when serializing, ujson converts datetime objects to epoch
                prop = getattr(all_models[model_name], field).property
                if hasattr(prop, 'columns') and isinstance(prop.columns[0].type, TIMESTAMP):
                    if value:
                        setattr(model, field, datetime.fromtimestamp(value))
                # defer F.Ks to later
                elif isinstance(value, dict):
                    not_serialized.append(value)
                # defer Back references to later
                elif isinstance(value, list):
                    not_serialized.extend(value)
                else:
                    setattr(model, field, value)
            return model, not_serialized

        serialized = [data]
        deserialized = []

        while serialized:
            data = serialized.pop()
            model, raw = deserialize(data)
            deserialized.append(model)
            serialized.extend(raw)
        return deserialized
