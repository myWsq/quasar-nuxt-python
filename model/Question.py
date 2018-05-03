from mongoengine import *
from mongoengine.errors import DoesNotExist
import graphene
from model.Survey import Survey, SurveyObject
from . import _mongo_to_graphene, _graphene_to_mongo


class Question(Document):
    title = StringField(required=True)
    type = StringField(required=True, choices=['单项选择题', '多项选择题', '填空题'])
    required = BooleanField(required=True, default=True)  # 是否必答
    survey = ReferenceField(Survey, required=True, reverse_delete_rule=CASCADE)
    option = StringField(required=True)  # 提供选择题选项 以'|'分割

    @property
    def graphene(self):
        survey = self.survey.graphene
        tmp = _mongo_to_graphene(self, QuestionObject)
        tmp.survey = survey
        return tmp


class QuestionObject(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    type = graphene.String()
    required = graphene.Boolean()
    option = graphene.String()
    survey = graphene.Field(SurveyObject)


class QuestionInput(graphene.InputObjectType):
    title = graphene.String()
    type = graphene.String()
    required = graphene.Boolean()
    option = graphene.String()
    survey_id = graphene.String()

    @property
    def mongo(self):
        tmp = _graphene_to_mongo(self, Question)
        tmp.survey = Survey.objects.get(id=self.survey_id)
        return tmp


class CreateQuestion(graphene.Mutation):
    class Arguments:
        question_input = QuestionInput(required=True)

    Output = QuestionObject

    @staticmethod
    def mutate(root, info, question_input):
        return question_input.mongo.save().graphene


class DeleteQuestion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    Output = graphene.Int

    @staticmethod
    def mutate(root, info, id):
        Question.objects.get(id=id).delete()
        return 1


class UpdateQuestion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        question_input = QuestionInput(required=True)

    Output = QuestionObject

    @staticmethod
    def mutate(root, info, id, question_input):
        Question.objects.get(id=id)
        tmp = question_input.mongo
        tmp.id = id
        return tmp.save().graphene


def get_question_by_survey_id():
    def resolve(root, info, survey_id):
        survey = Survey.objects.get(id=survey_id)
        return map(lambda x: x.graphene, Question.objects(survey=survey))

    return graphene.List(QuestionObject, survey_id=graphene.ID(required=True), resolver=resolve)


def get_question_by_id():
    def resolve(root, info, id):
        return Question.objects.get(id=id).graphene

    return graphene.Field(QuestionObject, id=graphene.ID(required=True), resolver=resolve)
