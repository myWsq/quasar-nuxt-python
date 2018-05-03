def _graphene_to_mongo(graphnen, mongo):
    tmp = mongo()
    for k, v in graphnen.__dict__.items():
        try:
            if tmp._fields.__contains__(k):
                tmp.__setattr__(k, v)
            else:
                continue
        except Exception:
            continue
    return tmp


def _mongo_to_graphene(mongo, graphene):
    tmp = graphene()
    for k in mongo._fields:
        try:
            tmp.__setattr__(k, getattr(mongo, k))
        except Exception:
            continue
    return tmp


from model import User, Question, Survey, Answer
from mongoengine import connect

_author__ = 'myWsq'
__all__ = ['User', 'Question', 'Survey', 'Answer']
connect('test', connect=False)
