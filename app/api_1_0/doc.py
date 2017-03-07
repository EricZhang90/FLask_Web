from . import api
from flask import render_template
from markdown import markdown



class API:
    def __init__(self, endpoint, description, request, response, note):
        self.endpoint = endpoint
        self.description = description

        def convertToHTML(value):
            return markdown(value, output_format='html')

        self.request = convertToHTML(request)
        self.response = convertToHTML(response)
        self.note = convertToHTML(note)


@api.route('/API_Doc')
def api_doc():
    return render_template('api_doc.html', apis=create_API_Documents())


def create_API_Documents():
    apis = []
    apis.append( API("USERS  &nbsp<strong>[GET]</strong>",
                     "Get a specific user by id",
                     "URL:  http://eric909.pythonanywhere.com/api/v1.0/user/<id>",
                     "JSON:\n\n \
                     {\n\n \
                        'url': '{URL}',\n\n \
                        'username': '{String}',\n\n \
                        'registered_date': '{Date}',\n\n \
                        'posts': '{URL}', \n\n \
                        'followed_posts': '{URL}', \n\n \
                        'posts_count': '{Int}', \n\n \
                        'followed': '{URL}', \n\n \
                        'followed_count': '{Int}', \n\n \
                        'followers': '{URL}', \n\n \
                        'followers_count': '{Int}' \n\n \
                    }\n\n",
                    "-"
                 )
    )
    apis.append( API("Comment  &nbsp<strong>[GET]</strong>",
                     "Get a specific comment by id",
                     "URL:  http://eric909.pythonanywhere.com/api/v1.0/comments/<id>",
                     "JSON:\n\n \
                     {\n\n \
                        'url': '{URL}',\n\n \
                        'post': {URL}',\n\n \
                        'body': {String}',\n\n \
                        'body_html': {HTML}',\n\n \
                        'timestamp': '{Date}',\n\n \
                        'author': {URL}',\n\n \
                     }\n\n",
                     "-"
                 )
    )
    apis.append( API("Posts  &nbsp<strong>[POST]</strong>",
                     "Upload a post",
                     "JSON\n\n \
                     {\n\n \
                        'body': '{String}'\n\n \
                     }\n\n",
                     "JSON:\n\n \
                     {\n\n \
                        'Location': {URL}',\n\n \
                     }\n\n",
                     "\n\n \
                      Authentication required.\n\n \
                      User write permission required.\n\n \
                      Upload context in body.\n\n \
                      Receive url pointing to generated post."
                 )
    )
    apis.append( API("Posts  &nbsp<strong>[PUT]</strong>",
                     "Modify a post",
                     "JSON\n\n \
                     {\n\n \
                        'body': '{String}'\n\n \
                     }\n\n",
                     "JSON:\n\n \
                     {\n\n \
                        'url': {URL}',\n\n \
                        'body': '{String}'\n\n \
                        'body_html': '{HTML}'\n\n \
                        'timestamp': '{Date}',\n\n \
                        'author': {URL}',\n\n \
                        'comments': {URL}',\n\n \
                        'comment_count': {Int}',\n\n \
                     }\n\n",
                     "\n\n \
                      Authentication required.\n\n \
                      User write permission required.\n\n \
                      Upload context in body.\n\n \
                      Receive modified post."
                 )
    )
    return apis












