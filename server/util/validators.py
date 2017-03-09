from server.util.exceptions import AppException

def songs_request_valid(request):
    if 'title' not in request:
    	raise AppException('error', 'song_title_missing', 'Title of the song is missing', status_code=400)
    if 'text' not in request:
    	raise AppException('error', 'song_text_missing', 'Text of the song is missing.', status_code=400)

    return True
