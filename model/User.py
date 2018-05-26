from mongoengine import ObjectIdField, StringField, DateTimeField, Document
from mongoengine.errors import DoesNotExist
import datetime
import graphene
from . import _mongo_to_graphene, _graphene_to_mongo


class User(Document):
    phone_number = StringField(required=True, unique=True, null=False)
    name = StringField(required=True, null=False)
    password = StringField(required=True, null=False)
    create_time = DateTimeField(default=datetime.datetime.now)

    @property
    def graphene(self):
        tmp = _mongo_to_graphene(self, UserObject)
        tmp.auth_token = self.id
        return tmp


class UserObject(graphene.ObjectType):
    auth_token = graphene.ID()
    phone_number = graphene.String()
    name = graphene.String()
    password = graphene.String()
    create_time = graphene.String()


def check_phone():
    def resolve(root, info, phone_number):
        try:
            User
            User.objects.get(phone_number=phone_number)
            return False
        except DoesNotExist:
            return True

    return graphene.Boolean(phone_number=graphene.String(required=True), resolver=resolve)


def login():
    def resolve(root, info, auth_token=None, phone_number=None, password=None):
        if not (auth_token or (phone_number and password)):
            raise ValueError('At least one param [ auth_token , phone_number , password ]')
        elif auth_token:
            user = User.objects.get(id=auth_token)
        else:
            user = User.objects.get(phone_number=phone_number, password=password)
        return user.graphene

    return graphene.Field(
        UserObject,
        auth_token=graphene.ID(required=False),
        phone_number=graphene.String(required=False),
        password=graphene.String(required=False),
        resolver=resolve
    )


class Reset(graphene.Mutation):
    class Arguments:
        auth_token = graphene.ID()
        phone_number = graphene.String()
        password = graphene.String(required=True)

    Output = UserObject

    @staticmethod
    def mutate(root, info, auth_token=None, phone_number=None, password=None):
        if not ((auth_token and password) or (phone_number and password)):
            raise ValueError('At least one param : [ auth_token , phone_number ] ')
        if auth_token:
            user = User.objects.get(id=auth_token)
        else:
            user = User.objects.get(phone_number=phone_number)
        user.password = password
        return user.save().graphene


class SignUp(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = UserObject

    @staticmethod
    def mutate(root, info, name, phone_number, password):
        tmp = User(name=name, phone_number=phone_number, password=password).save()
        return tmp.graphene
