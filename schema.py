from graphene import *
from model import *


class Query(ObjectType):
    # User
    login = User.login()
    check_phone = User.check_phone()
    # Survey
    surveys = Survey.get_survey_by_auth_token()
    survey = Survey.get_survey_by_id()
    # Question
    questions = Question.get_question_by_survey_id()
    question = Question.get_question_by_id()
    # Answer
    answers = Answer.get_answer_by_question_id()
    answer_num = Answer.get_answer_number_by_survey_id()

class Mutation(ObjectType):
    # User
    sign_up = User.SignUp.Field()
    reset = User.Reset.Field()
    # Survey
    create_survey = Survey.CreateSurvey.Field()
    delete_survey = Survey.DeleteSurvey.Field()
    update_survey = Survey.UpdateSurvey.Field()
    # Question
    create_question = Question.CreateQuestion.Field()
    delete_question = Question.DeleteQuestion.Field()
    update_question = Question.UpdateQuestion.Field()
    # Answer
    create_answer = Answer.CreateAnswers.Field()


schema = Schema(query=Query, mutation=Mutation)
