import click
import os
import requests
from shub import auth
from six.moves import input

VALIDATE_API_KEY_ENDPOINT = "https://dash.scrapinghub.com/api/v2/users/me"

@click.command(help='add Scrapinghug API key into the netrc file')
@click.pass_context
def cli(context):
    if auth.get_key_netrc():
        click.echo("You're already logged in. To change credentials, use 'shub logout' first.")
        return 0

    cfg_key = _find_cfg_key()
    key = _get_apikey(suggestion=cfg_key)
    auth.write_key_netrc(key)


def _get_apikey(suggestion=''):
    suggestion_txt = ' (%s)' % suggestion if suggestion else ''
    click.echo('Enter your API key from https://dash.scrapinghub.com/account/apikey')
    key = ''
    while True:
        key = input('API key%s: ' % suggestion_txt)
        click.echo("Validating API key...")
        r = requests.get("%s?apikey=%s" % (VALIDATE_API_KEY_ENDPOINT, key))
        if r.status_code == 200:
            click.echo("API key is OK, you are logged in now.")
            return key
        else:
            click.echo("API key failed, try again.")


def _find_cfg_key():
    cfg_key = _read_scrapy_cfg_key()
    if cfg_key:
        return cfg_key

    envkey = os.getenv("SHUB_APIKEY")
    if envkey:
        return envkey

def _read_scrapy_cfg_key():
    try:
        from scrapy.utils.conf import get_config
        cfg = get_config()

        if cfg.has_section('deploy'):
            deploy = dict(cfg.items('deploy'))
            key = deploy.get('username')

            if key:
                return key
    except:
        return
