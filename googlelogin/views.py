import datetime
import os
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from googlelogin.models import GoogleAccount


class GoogleLoginView(LoginRequiredMixin, TemplateView, ):
    template_name = 'googlelogin/home.html'


# doc: https://developers.google.com/my-business/reference/accountmanagement/rest/v1/accounts/list
API_SERVICE_NAME = 'mybusinessaccountmanagement'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/business.manage']
CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES_DB_DELIMITER = ';'

# todo R: remove it in production. It suppresses OAUTH HTTPS verification
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@login_required
def authorize(request):
    flow = _create_auth_flow(request)
    authorization_url, state = flow.authorization_url(access_type='offline', prompt='select_account',
                                                      include_granted_scopes='true')
    request.session['state'] = state
    return redirect(authorization_url)


@login_required
def authorize_callback(request):
    state = request.session['state']
    flow = _create_auth_flow(request, state)
    flow.fetch_token(authorization_response=(request.build_absolute_uri()))
    google_account = _convert_credentials_to_google_account(request.user, flow.credentials)
    google_account.save()
    return HttpResponse('<a href="/" class="button">The google account was successfully stored!</a>')


@login_required
def get_all_accounts(request):
    try:
        google_account = GoogleAccount.objects.get(user_id=request.user)
        credentials = _convert_google_account_to_credentials(google_account)
        service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        accounts_list = service.accounts().list().execute()
        google_account = _convert_credentials_to_google_account(request.user, credentials)
        google_account.save()
        return HttpResponse(f'The number of accounts is = {len(accounts_list)}')
    except GoogleAccount.DoesNotExist:
        return redirect(reverse('authorize'))


def _create_auth_flow(request, state=None):
    kwargs = {}
    if state is not None:
        kwargs['state'] = state

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, **kwargs)
    flow.redirect_uri = request.build_absolute_uri(reverse('authorize_callback'))
    return flow


def _convert_credentials_to_google_account(user, credentials):
    return GoogleAccount(user=user, token=credentials.token,
                         refresh_token=credentials.refresh_token,
                         token_uri=credentials.token_uri,
                         client_id=credentials.client_id,
                         client_secret=credentials.client_secret,
                         scopes=SCOPES_DB_DELIMITER.join(credentials.scopes),
                         updated_datetime=datetime.datetime.now())


def _convert_google_account_to_credentials(account):
    return google.oauth2.credentials.Credentials(token=account.token, refresh_token=account.refresh_token,
                                                 token_uri=account.token_uri, client_id=account.client_id,
                                                 client_secret=account.client_secret,
                                                 scopes=account.scopes.split(SCOPES_DB_DELIMITER))
