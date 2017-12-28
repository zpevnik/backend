import json


# post interpreter into the database
def _post_interpreter(app, name='name'):
    return app.post(
        '/api/v1/interpreters', content_type='application/json', data=json.dumps(dict(name=name)))


# post author into the database
def _post_author(app, name='name'):
    return app.post(
        '/api/v1/authors', content_type='application/json', data=json.dumps(dict(name=name)))


# post author into the database
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
                text=text,
                description=description,
                authors={'lyrics': lauthors,
                         'music': mauthors},
                interpreters=interpreters)))


# put author into the database
def _put_song(app,
              song_id,
              title='title',
              text='[verse]',
              description='',
              lauthors=[],
              mauthors=[],
              interpreters=[],
              visibility=None,
              edit_perm=None):
    data = {
        'title': title,
        'text': text,
        'description': description,
        'authors': {
            'lyrics': lauthors,
            'music': mauthors
        },
        'interpreters': interpreters
    }
    if visibility is not None:
        data['visibility'] = visibility
    if edit_perm is not None:
        data['edit_perm'] = edit_perm

    return app.put(
        '/api/v1/songs/{}'.format(song_id), content_type='application/json', data=json.dumps(data))
