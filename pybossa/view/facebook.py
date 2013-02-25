# This file is part of PyBOSSA.
#
# PyBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBOSSA.  If not, see <http://www.gnu.org/licenses/>.

from flask import Blueprint, request, url_for, flash, redirect, session
from flaskext.login import login_user, current_user

import pybossa.model as model
from pybossa.core import db
from pybossa.util import Facebook
# Required to access the config parameters outside a context as we are using
# Flask 0.8
# See http://goo.gl/tbhgF for more info
from pybossa.core import app

# This blueprint will be activated in web.py if the FACEBOOK APP ID and SECRET
# are available
blueprint = Blueprint('facebook', __name__)
facebook = Facebook(app.config['FACEBOOK_APP_ID'],
                    app.config['FACEBOOK_APP_SECRET'])


@blueprint.route('/', methods=['GET', 'POST'])
def login():
    return facebook.oauth.authorize(callback=url_for('.oauth_authorized',
                                                     next=request.args.get("next"),
                                                     _external=True))


@facebook.oauth.tokengetter
def get_facebook_token():
    if current_user.is_anonymous():
        return session.get('oauth_token')
    else:
        return (current_user.info['facebook_token']['oauth_token'], '')


@blueprint.route('/oauth-authorized')
@facebook.oauth.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('home')
    if resp is None:
        flash(u'You denied the request to sign in.', 'error')
        flash(u'Reason: ' + request.args['error_reason'] +
              ' ' + request.arts['error_description'], 'error')
        return redirect(next_url)

    # We have to store the oauth_token in the session to get the USER fields
    access_token = resp['access_token']
    session['oauth_token'] = (resp['access_token'], '')
    user_data = facebook.oauth.get('/me').data

    user = manage_user(access_token, user_data, next_url)
    if user is None:
        # Give a hint for the user
        user = db.session.query(model.User)\
                 .filter_by(email_addr=user_data.data['email'])\
                 .first()
        msg = u'Sorry, there is already an account with the same e-mail.'
        if user.info.get('google_token'):
            msg += " It seems like you signed up with your Google account."
            msg += "<br/>You can try and sign in by clicking in the Google button."
            flash(msg, 'info')
            return redirect(url_for('account.signin'))
        elif user.info.get('twitter_token'):
            msg += " It seems like you signed up with your Twitter account."
            msg += "<br/>You can try and sign in by clicking in the Twitter button."
            flash(msg, 'info')
            return redirect(url_for('account.signin'))
        else:
            msg += " It seems that you created an account locally in %s." % app.config['BRAND']
            msg += " <br/>You can reset your password if you don't remember it."
            flash(msg, 'info')
            return redirect(url_for('account.forgot_password'))
    else:
        first_login = False
        login_user(user, remember=True)
        flash("Welcome back %s" % user.fullname, 'success')
        request_email = False
        if (user.email_addr == "None"):
            request_email = True
        if request_email:
            if first_login:
                flash("This is your first login, please add a valid e-mail")
            else:
                flash("Please update your e-mail address in your profile page")
            return redirect(url_for('account.update_profile'))
        return redirect(next_url)


def manage_user(access_token, user_data, next_url):
    """Manage the user after signin"""
    user = db.session.query(model.User)\
             .filter_by(facebook_user_id=user_data['id']).first()

    if user is None:
        facebook_token = dict(oauth_token=access_token)
        info = dict(facebook_token=facebook_token)
        user = db.session.query(model.User)\
                 .filter_by(name=user_data['username']).first()
        email = db.session.query(model.User)\
                  .filter_by(email_addr=user_data['email']).first()

        if user is None and email is None:
            user = model.User(fullname=user_data['name'],
                              name=user_data['username'],
                              email_addr=user_data['email'],
                              facebook_user_id=user_data['id'],
                              info=info)
            db.session.add(user)
            db.session.commit()
            return user
        else:
            return None
    else:
        return user
