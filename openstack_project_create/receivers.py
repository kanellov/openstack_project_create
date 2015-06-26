from django.dispatch import receiver
from signals import sch_create_project

@receiver(project_created)
def project_networking(sender, **kwargs):
    return True
