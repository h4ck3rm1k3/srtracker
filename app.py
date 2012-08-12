import os
from flask import Flask, render_template, request, abort, redirect, url_for, make_response, session
import requests
import iso8601
import updater

import logging
fileHandler = logging.FileHandler('application2.log')
logger = logging.getLogger('TESTHARNESSFILE')
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)
import pprint
pp = pprint.PrettyPrinter(indent=4)


# Config
DEBUG = True
OPEN311_SERVER = 'http://localhost:5000'
OPEN311_API_KEY = ''
PASSWORD_PROTECTED = False
SECRET_KEY = 'please_please_change_this!'

app = Flask(__name__)

@app.before_request
def password_protect():
    if app.config['PASSWORD_PROTECTED']:
        auth = request.authorization
        if not auth or auth.password != app.config['PASSWORD']:
            # Tell the browser to do basic auth
            return make_response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})


def debugrequest (r):
    logger.debug("Request form %s" % pp.pformat(r.form))            
    logger.debug("Request args %s" % pp.pformat(r.args))            
    logger.debug("Request values %s" % pp.pformat(r.values))            
    logger.debug("Request data %s" % pp.pformat(r.data))            
    logger.debug("Request url %s" % pp.pformat(r.url))            
    logger.debug("Request headers %s" % pp.pformat(r.headers))            
    logger.debug("Request env %s" % pp.pformat(r.environ))            
    # r.cookies
    # r.stream
    # r.files
    # r.method
    # r.path
    # r.script_root
    # r.base_url
    # r.url_root

def debugresponse (r)    :
    logger.debug("Response %s" % pp.pformat(r))            
    logger.debug("Response Header %s" % pp.pformat(r.headers))            
    logger.debug("Response Status code %s" % pp.pformat(r.status_code))            
    logger.debug("Response content %s" % pp.pformat(r.content))            

@app.route("/")
def index():
    url = '%s/requests.json' % app.config['OPEN311_SERVER']
    params = {'extensions': 'true', 'legacy': 'false'}
    if app.config['OPEN311_API_KEY']:
        params['api_key'] = app.config['OPEN311_API_KEY']
        
    logger.debug("Server: %s" % app.config['OPEN311_SERVER'])            
    logger.debug("Going to request url %s" % pp.pformat(url))            
    logger.debug("going to request with params: %s" % pp.pformat(params))            

    r = requests.get(url, params=params)

    if 'request_id' in request.args:
        request_id =request.args['request_id']
    else :
        request_id ="unknown"

    try  :
        service_requests=r.json
        logger.debug("service_requests %s" % pp.pformat(service_requests))            

    except :
        logger.error("There was an error in the 311 service request response")
        debugresponse (r)
        debugrequest (request)
        return ("There was an error in the 311 service request response", 500, None)

    if r.status_code != 200:
        # TODO: need a template
        logger.error("There was an error getting service request data for request id : %s ." % request_id)
        debugresponse (r)
        debugrequest (request)
        return ("There was an error getting service request data for request id : %s ." % request_id, 500, None)

    return render_template('index.html', sr=service_requests)


@app.route("/requests")
def redirect_request():
    if 'request_id' in request.args:
        request_id =request.args['request_id']
        return redirect(url_for('show_request', request_id=request_id))
    else:
        abort(404)


@app.route("/requests/<request_id>")
def show_request(request_id):
    request_id = request_id.lstrip('#')
    
    # TODO: Should probably use Three or something nice for this...
    url = '%s/requests/%s.json' % (app.config['OPEN311_SERVER'], request_id)
    params = {'extensions': 'true', 'legacy': 'false'}
    if app.config['OPEN311_API_KEY']:
        params['api_key'] = app.config['OPEN311_API_KEY']
    r = requests.get(url, params=params)
    if r.status_code == 404:
        # TODO: need a template
#        logger.error("There is no service request on file for #%s" % request_id)
#        debugresponse (r)
#        debugrequest (request)    
        return render_template('no_service_request_found.html', rid=request_id)
        
    elif r.status_code != 200:
        # TODO: need a template
        logger.error("There was an error getting data about service request #%s" % request_id)
        debugresponse (r)
        debugrequest (request)    
        return ("There was an error getting data about service request #%s" % request_id, 404, None)
        
    srs = r.json
    if srs:
        sr = srs[0]
        sr['requested_datetime'] = iso8601.parse_date(sr['requested_datetime'])
        for note in sr['notes']:
            note['datetime'] = iso8601.parse_date(note['datetime'])
        
        # add follow-on closure data
        by_id = {}
        for note in sr['notes']:
            if note['type'] == 'follow_on':
                note_sr_id = note['extended_attributes']['service_request_id']
                if note_sr_id in by_id:
                    if note['description'].endswith('Closed'):
                        original = by_id[note_sr_id]
                        original['extended_attributes']['closed_datetime'] = note['datetime']
                else:
                    by_id[note_sr_id] = note
        
        sr['notes'].reverse()
        
        subscribed = False
        if sr['status'] == 'open' and session.get('email', None):
            # TODO: when subscription service supports more than e-mail, 
            # we should probably be able to show all your subscriptions here
            subscribed = updater.subscription_exists(request_id, 'email', session.get('email', ''))
        
        body = render_template('service_request.html', sr=sr, subscribed=subscribed)
        return (body, 200, None)
    
    else:
        return render_template('no_service_request_found.html', rid=request_id)


@app.route("/subscribe/<request_id>", methods=["POST"])
def subscribe(request_id):
    email = request.form.get('update_email')
    # TODO: validate email
    if email:
        updater.subscribe(request_id, 'email', email)
        # TODO: should we get back a secret subscription key and use that instead?
        session['email'] = email
    return redirect(url_for('show_request', request_id=request_id))



if __name__ == "__main__":
    app.config.from_object(__name__)
    app.debug = os.environ.get('DEBUG', str(app.debug)) == 'True'
    app.secret_key = os.environ.get('SECRET_KEY', app.secret_key)
    app.config['OPEN311_SERVER'] = os.environ.get('OPEN311_SERVER', OPEN311_SERVER)
    app.config['OPEN311_API_KEY'] = os.environ.get('OPEN311_API_KEY', OPEN311_API_KEY)
    app.config['PASSWORD_PROTECTED'] = os.environ.get('PASSWORD_PROTECTED', str(PASSWORD_PROTECTED)) == 'True'
    app.config['PASSWORD'] = os.environ.get('PASSWORD', '')
    
    port = int(os.environ.get('PORT', 5100))
    app.run(host='0.0.0.0', port=port)
    
