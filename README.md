# Installation

    pip install hg+http://10.2.46.23/source/schcloud/project_creator/@default#egg=openstack_project_create

# Configuration
Insert into ```/etc/openstack-dashboard/local_settings.py``` the following and change
to apropriate values.

    CREATE_PROJECT = {
        "ADMIN_DOMAIN_NAME": "default",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "",
        "ADMIN_PROJECT_NAME": "admin",
        "ADMIN_AUTH_URL":  "http://%s:35357/v3" % OPENSTACK_HOST,
        "AFFECTED_DOMAINS": ["default"],
        "DEFAULT_ROLES": ["_member_"],
        "PROJECT_NAME_TEMPLATE": "%s Project",
        "PROJECT_DESC_TEMPLATE": "Auto created Project for %s",
    }
    ADD_INSTALLED_APPS = ['openstack_project_create']

