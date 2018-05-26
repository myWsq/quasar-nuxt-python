from flask import Flask
from flask_graphql import GraphQLView
from schema import schema
from flask_cors import CORS
from model.Answer import Answer
from model.Question import Question
import json
import bosonnlp
import os
import socket

app = Flask(__name__)
app.debug = True

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
nlp = bosonnlp.BosonNLP('N8QGyDTh.24543.aYEyRYQd0cxn')
CORS(app)


@app.route('/api/<question_id>')
def analyse(question_id):
    q = Question.objects.get(id=question_id)
    answers = Answer.objects(question=q)
    total = len(answers)
    if not total:
        raise KeyError
    if q.type == '单项选择题' or q.type == '多项选择题':
        tmp = {}
        for each in answers:
            tmp.setdefault(each.content, 0)
            tmp[each.content] += 1.0 / total
        return json.dumps(tmp)
    else:
        pass


@app.route('/api/sentiment/<question_id>')
def get_sentiment(question_id):
    q = Question.objects.get(id=question_id)
    if q.type == '填空题':
        contents = [each.content for each in Answer.objects(question=q)]
        if not len(contents):
            raise KeyError
        else:
            results = nlp.sentiment(contents)
            final = 0.0
            for item in results:
                final += item[0]
            final /= len(contents)
            return json.dumps(final)
    else:
        raise KeyError


@app.route('/api/keywords/<question_id>')
def get_keywords(question_id):
    q = Question.objects.get(id=question_id)
    if q.type == '填空题':
        content = ''
        for each in Answer.objects(question=q):
            content += (each.content + ' ')
        if not content:
            raise KeyError
        else:
            keywords = nlp.extract_keywords(content,top_k=50)
            return json.dumps(keywords)
    else:
        raise KeyError


@app.route('/api/comments/<question_id>')
def get_comments(question_id):
    q = Question.objects.get(id=question_id)
    if q.type == '填空题':
        contents = [each.content for each in Answer.objects(question=q)]
        if not contents:
            raise KeyError
        else:
            comments = nlp.comments(contents)
            return json.dumps(comments)
    else:
        raise KeyError


if __name__ == '__main__':
    # host = socket.gethostbyname(socket.gethostname()) + ':8888'
    # img = qrcode.make('http://'+'m.mywsq.cn')
    # img.save('host.png')
    # os.system('open %s' % os.path.join(os.path.dirname(__file__), 'host.png'))
    # # # print('Your app is running on [%s]' % host)
    app.run(host='0.0.0.0', port=8081)
