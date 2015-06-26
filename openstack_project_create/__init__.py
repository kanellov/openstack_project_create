from django.conf import settings

import signals
# import receivers

settings.MIDDLEWARE_CLASSES += (
    'openstack_project_create.middleware.CreateProject',
)
