import os
from quart import Quart
from officepong.routes import officepong_app
from tortoise.contrib.quart import register_tortoise
def create_app():

    app = Quart(__name__)
    app.config.from_object('officepong.default_settings')
    app.config.from_prefixed_env()

    if "OFFICEPONG_SETTINGS" in os.environ:
        app.config.from_envvar("OFFICEPONG_SETTINGS")
    
    if not app.config.get('TORTOISE_CONFIG'):
        app.config['TORTOISE_CONFIG'] = {
            'connections': {
                'default': f'{app.config["TORTOISE_DB_URL"]}'
            },
            'apps': {
                'models': {
                    'models': ["officepong.models"],
                    'default_connection': 'default',
                }
            }
        }

    app.register_blueprint(officepong_app)

    register_tortoise(
        app=app,
        config=app.config['TORTOISE_CONFIG'],
        generate_schemas=False,
    )

    return app
