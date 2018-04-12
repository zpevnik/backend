import json


# post interpreter into the database
def _post_interpreter(app, name='name'):
    return app.post(
        '/api/v1/interpreters', content_type='application/json', data=json.dumps(dict(name=name)))


# put interpreter into the database
def _put_interpreter(app, interpreter_id, name='name'):
    return app.put(
        '/api/v1/interpreters/{}'.format(interpreter_id),
        content_type='application/json',
        data=json.dumps(dict(name=name)))


# post author into the database
def _post_author(app, name='name'):
    return app.post(
        '/api/v1/authors', content_type='application/json', data=json.dumps(dict(name=name)))


# put author into the database
def _put_author(app, author_id, name='name'):
    return app.put(
        '/api/v1/authors/{}'.format(author_id),
        content_type='application/json',
        data=json.dumps(dict(name=name)))


# post song into the database
def _post_song(app,
               title='title',
               text='[verse]',
               description='',
               lauthors=[],
               mauthors=[],
               interpreters=[]):
    return app.post(
        '/api/v1/songs',
        content_type='application/json',
        data=json.dumps(
            dict(
                title=title,
                authors={'lyrics': lauthors,
                         'music': mauthors},
                interpreters=interpreters,
                variant={
                    'text': text,
                    'description': description
                })))


# post songbook into the database
def _post_songbook(app, title='title'):
    return app.post(
        '/api/v1/songbooks', content_type='application/json', data=json.dumps(dict(title=title)))


# put song into the database
def _put_song(app, song_id, title='title', lauthors=[], mauthors=[], interpreters=[]):
    data = {
        'title': title,
        'authors': {
            'lyrics': lauthors,
            'music': mauthors
        },
        'interpreters': interpreters
    }
    return app.put(
        '/api/v1/songs/{}'.format(song_id), content_type='application/json', data=json.dumps(data))


# put song variant into the database
def _put_song_variant(app, song_id, variant_id, text='[verse]', description="", visibility=None):
    data = {'text': text, 'description': description}
    if visibility is not None:
        data['visibility'] = visibility

    return app.put(
        '/api/v1/songs/{}/variants/{}'.format(song_id, variant_id),
        content_type='application/json',
        data=json.dumps(data))


# put songbook into the database
def _put_songbook(app, songbook_id, title='title', songs=[], options={}):
    return app.put(
        '/api/v1/songbooks/{}'.format(songbook_id),
        content_type='application/json',
        data=json.dumps(dict(title=title, songs=songs, options=options)))


# put songbook title into the database
def _put_songbook_title(app, songbook_id, title='title'):
    return app.put(
        '/api/v1/songbooks/{}/title'.format(songbook_id),
        content_type='application/json',
        data=json.dumps(dict(title=title)))


# put songbook song list into the database
def _put_songbook_songs(app, songbook_id, songs=[]):
    return app.put(
        '/api/v1/songbooks/{}/songs'.format(songbook_id),
        content_type='application/json',
        data=json.dumps(dict(songs=songs)))


# put songbook options into the database
def _put_songbook_options(app, songbook_id, options={}):
    return app.put(
        '/api/v1/songbooks/{}/options'.format(songbook_id),
        content_type='application/json',
        data=json.dumps(dict(options=options)))
