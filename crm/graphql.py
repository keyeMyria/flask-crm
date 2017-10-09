import graphene
from graphene.types.objecttype import ObjectType
from graphene.types.scalars import Scalar

from graphene_sqlalchemy.fields import SQLAlchemyConnectionField


class BaseMutation(graphene.ObjectType):
    """
    Base class for all Mutations
    """
    pass


class BaseQuery(graphene.ObjectType):
    """
    Base class for all Queries
    """
    pass


class CRMConnectionField(SQLAlchemyConnectionField):
    """
    Any query using CRMConnectionField will have its results 
    objects updated with a (uid) field containing the value of the 
    original db model id value.
    Reason is : graphene hodes id field with another internal representation
    and in some cases we may need our original id to appear so we put it as uid    
    """
    def __init__(self, *args, **kwargs):
        super(CRMConnectionField, self).__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        result = SQLAlchemyConnectionField.connection_resolver(*args, **kwargs)
        for e in result.iterable:
            e.uuid = e.uid
        return result


class ErrorType(ObjectType):
    message = graphene.String()
    def __init__(self, message):
        self.message = message

class GraphqlError(graphene.ObjectType):
    message = graphene.Field(ErrorType)


