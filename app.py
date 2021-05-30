import os
from flask import Flask, request, json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def assignment():
    return 'Assignment 4!'


@app.route('/news_api')
def news_api():
    with app.open_resource('static/yahoo-news.json') as f:
        json_news = json.load(f)
    key_words = request.args.get('q')
    n_news = request.args.get('n')
    n_words = request.args.get('w')
    if key_words is not None:
        key_words = key_words.split(',')
        json_news = [a for a in json_news if all(k in a['title'] for k in key_words)
                     or all(k in a['content'] for k in key_words)]
    if n_news is not None:
        json_news = json_news[:int(n_news)]
    if n_words is not None:
        for news in json_news:
            news['content'] = news['content'][:int(n_words)]
    return json.jsonify(json_news)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
