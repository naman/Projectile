# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

import re

from django.contrib.auth.models import User
from django.utils import timezone


def is_member(user, group):
    """Checks if the user object is a member of the group or not."""
    return user.groups.filter(name=group)


def is_eligible(candidate, project):
    """
    Checks if the user object is a eligible candidate for the project or not.
    All the logic for checking eligibility goes here!
    """
    eligibility = {}
    eligibility['value'] = True
    # list of all the reasons that contribute towards uneligibilty
    eligibility['reasons'] = []

    if (candidate.cgpa < project.cgpa_min):
        eligibility['value'] = False
        eligibility['reasons'].append(
            "Your CGPA is below the requirement.")

    if (candidate.backlogs > project.max_blacklogs):
        eligibility['value'] = False
        eligibility['reasons'].append("You have too many backlogs.")

    if (project.status == 'C' or project.status == 'A'):
        eligibility['value'] = False
        eligibility['reasons'].append("This Project cannot be applied to.")

    return eligibility


def checkdeadline(project):
    """Checks if the deadline has passed or not."""
    if (timezone.now() > project.deadline):
        return True
    else:
        return False


def is_admin(user):
    """Checks if the user object is a member of the admin group or not."""
    allowed_group = {'admin'}
    usr = User.objects.get(username=user)
    groups = [x.name for x in usr.groups.all()]
    if allowed_group.intersection(set(groups)):
        return True
    return False


def special_match(strg, search=re.compile(r'[^A-Za-z0-9., -]').search):
    return not bool(search(strg))


def contact_match(strg, search=re.compile(r'[0-9]\n').search):
    return not bool(search(strg))


def onlyspecchar_match(strg, search=re.compile(r'^[., -]').search):
    return not bool(search(strg))


def onlynumbers(strg, search=re.compile(r'^[0-9]').search):
    return bool(search(strg))
