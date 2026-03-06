from flask import render_template
from my_server import app

def register_errorhandlers(app):
    @app.errorhandler(401)
    def unauthorized(e):
        return  render_template ("errors/401.html") , 401
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return "500 - Server error", 500
    

    