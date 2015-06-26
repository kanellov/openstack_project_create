from django.conf import settings
from django.core.urlresolvers import resolve
from django.dispatch import Signal
from six.moves.urllib import parse as urlparse
from keystoneclient.v3 import client as client_v3

import signals

import logging

LOG = logging.getLogger('django')
CONFIG = getattr(settings, 'CREATE_PROJECT')

def has_in_url_path(url, sub):
    """Test if the `sub` string is in the `url` path."""
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    return sub in path

def url_path_replace(url, old, new, count=None):
    """Return a copy of url with replaced path.

    Return a copy of url with all occurrences of old replaced by new in the url
    path.  If the optional argument count is given, only the first count
    occurrences are replaced.
    """
    args = []
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    if count is not None:
        args.append(count)
    return urlparse.urlunsplit((
        scheme, netloc, path.replace(old, new, *args), query, fragment))

def get_keystone_client(user_domain_name, username, password, project_name = None, auth_url = None):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    ca_cert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    if auth_url == None:
        auth_url = getattr(settings, 'OPENSTACK_KEYSTONE_URL', None)

    if has_in_url_path(auth_url, "/v2.0"):
        auth_url = url_path_replace(auth_url, "/v2.0", "/v3", 1)

    client = client_v3.Client(
            user_domain_name=user_domain_name,
            username=username,
            password=password,
            project_name=project_name,
            auth_url=auth_url,
            insecure=insecure,
            cacert=ca_cert,
            debug=settings.DEBUG)
    client.management_url = auth_url

    return  client

class CreateProject(object):

    _user_client = None
    _admin_client = None

    def user_client(self, request):
        if self._user_client == None:
            self._user_client = get_keystone_client(
                user_domain_name=request.POST.get('domain'),
                username=request.POST.get('username'),
                password=request.POST.get('password'),
                auth_url=request.POST.get('region'))
        return self._user_client

    def admin_client(self):
        if self._admin_client == None:
            self._admin_client = get_keystone_client(
                user_domain_name=CONFIG.get('ADMIN_DOMAIN_NAME', None),
                username=CONFIG.get('ADMIN_USERNAME', None),
                password=CONFIG.get('ADMIN_PASSWORD', None),
                project_name=CONFIG.get('ADMIN_PROJECT_NAME', None),
                auth_url=CONFIG.get('ADMIN_AUTH_URL', None))
        return self._admin_client


    def process_request(self, request):
        current_url = resolve(request.path_info).url_name
        affected_domains = CONFIG.get('AFFECTED_DOMAINS', [])
        domain = request.POST.get('domain', False)
        if request.method == 'POST' and domain in affected_domains and current_url == 'login':
            project = None
            try:
                user_client = self.user_client(request);
                auth_ref = user_client.auth_ref
                projects = user_client.projects.list(user=auth_ref.user_id)
                if not projects:
                    admin_client = self.admin_client()
                    project_name = CONFIG.get(
                        'PROJECT_DESC_NAME',
                        '%s Project') % auth_ref.username
                    project_description = CONFIG.get(
                        'PROJECT_DESC_TEMPLATE',
                        'Auto created Project for %s') % auth_ref.username
                    project = admin_client.projects.create(
                        name=project_name, domain=auth_ref.user_domain_id,
                        description=project_description)
                    for role in CONFIG.get('DEFAULT_ROLES', ['_member_']):
                        match = admin_client.roles.list(name=role)
                        if len(match) == 0:
                            continue
                        role = match[0]
                        admin_client.roles.grant(
                            role=role, user=auth_ref.user_id, project=project)
                    responses = signals.project_created.send(
                        sender=self, project=project, user_id=auth_ref.user_id)
                    if not all(map(lambda res: res[1], responses)):
                        raise Exception
                    LOG.debug("Project created for user %s" % request.POST.get('username'))
            except Exception as e:
                if project != None:
                    admin_client.projects.delete(project.id)

                LOG.error("Unable to create project for user %s" % request.POST.get('username'))
                raise

        return None

