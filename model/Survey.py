from mongoengine import *
from .User import User, UserObject
import datetime
import graphene
from . import _mongo_to_graphene, _graphene_to_mongo


class Survey(Document):
    creator = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    title = StringField(required=True)
    description = StringField(required=True)
    release = BooleanField(required=False, default=False)
    create_datetime = DateTimeField(default=datetime.datetime.now)  # 问卷创建时间

    @property
    def graphene(self):
        tmp = _mongo_to_graphene(self, SurveyObject)
        tmp.creator = self.creator.graphene
        tmp.create_datetime = str(self.create_datetime.timestamp())
        return tmp


class SurveyObject(graphene.ObjectType):
    id = graphene.ID()
    creator = graphene.Field(UserObject)
    title = graphene.String()
    description = graphene.String()
    create_datetime = graphene.String()
    release = graphene.Boolean()


class SurveyInput(graphene.InputObjectType):
    auth_token = graphene.ID(required=True)
    title = graphene.String(required=True)
    description = graphene.String(required=True)
    release = graphene.Boolean(required=False)

    @property
    def mongo(self):
        user = User.objects.get(id=self.auth_token)
        tmp = _graphene_to_mongo(self, Survey)
        tmp.creator = user
        return tmp


class UpdateSurvey(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        survey_input = SurveyInput(required=True)

    Output = SurveyObject

    @staticmethod
    def mutate(root, info, id, survey_input):
        survey = Survey.objects.get(id=id)
        survey.title = survey_input.title
        survey.description = survey_input.description
        survey.release = survey_input.release
        survey.save()
        return survey.graphene


class CreateSurvey(graphene.Mutation):
    class Arguments:
        survey_input = SurveyInput(required=True)

    Output = SurveyObject

    @staticmethod
    def mutate(root, info, survey_input):
        return survey_input.mongo.save().graphene


class DeleteSurvey(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    Output = graphene.Int

    @staticmethod
    def mutate(root, info, id):
        Survey.objects.get(id=id).delete()
        return 1


def get_survey_by_auth_token():
    def resolve(root, info, auth_token):
        user = User.objects.get(id=auth_token)
        return map(lambda x: x.graphene, Survey.objects(creator=user))

    return graphene.List(SurveyObject, auth_token=graphene.ID(required=True), resolver=resolve)


def get_survey_by_id():
    def resolve(root, info, id):
        return Survey.objects.get(id=id).graphene

    return graphene.Field(SurveyObject, id=graphene.ID(required=True), resolver=resolve)
