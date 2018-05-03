from mongoengine import *
import graphene
from model.User import User, UserObject
from model.Question import Question, QuestionObject
from . import _mongo_to_graphene, _graphene_to_mongo
from functools import reduce


class Answer(Document):
    question = ReferenceField(Question, required=True)
    content = StringField(required=False)  # 填空题答案

    @property
    def graphene(self):
        tmp = _mongo_to_graphene(self, QuestionObject)
        tmp.question = self.question.graphene
        return tmp


class AnswerObject(graphene.ObjectType):
    id = graphene.ID()
    question = graphene.Field(QuestionObject)
    content = graphene.String()


class AnswerInput(graphene.InputObjectType):
    question_id = graphene.String(required=True)
    content = graphene.String(required=True)

    @property
    def mongo(self):
        question = Question.objects.get(id=self.question_id)
        tmp = _graphene_to_mongo(self, Answer)
        tmp.question = question
        return tmp


def get_answer_by_question_id():
    def resolve(root, info, question_id):
        return map(lambda x: x.graphene, Answer.objects(question=question_id))

    return graphene.List(AnswerObject, question_id=graphene.ID(required=True), resolver=resolve)


def get_answer_number_by_survey_id():
    def resolve(root, info, survey_id):
        return reduce(lambda x, y: x + y, map(lambda x: Answer.objects.filter(question=x.id).count(),
                                              Question.objects.filter(survey=survey_id)))

    return graphene.Int(survey_id=graphene.ID(required=True), resolver=resolve)


class CreateAnswers(graphene.Mutation):
    class Arguments:
        answers_input = graphene.List(AnswerInput, required=True)

    Output = graphene.List(AnswerObject)

    @staticmethod
    def mutate(root, info, answers_input):
        return map(lambda x: x.mongo.save().graphene, answers_input)
