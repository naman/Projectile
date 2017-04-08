# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

import re

from django.contrib.auth.models import Group
from django.utils import timezone


def is_member(user, group):
    """Checks if the user object is a member of the group or not."""
    # return user.groups.filter(name=group)
    g = Group.objects.get(name=group)
    return g.user_set.filter(email=str(user.email))


def contains_group(user, group):
    g = Group.objects.get(name=group)
    if g in user.groups.all():
        return True
    return False


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
            "CGPA requirement not fulfilled.")

    # if (project.status == 'C' or project.status == 'A'):
    #     eligibility['value'] = False
    #     eligibility['reasons'].append("This Project cannot be applied to.")

    return eligibility


def checkdeadline(project):
    """Checks if the deadline has passed or not."""
    if (timezone.now() > project.deadline):
        return True
    else:
        return False


def is_admin(user):
    """Checks if the user object is a member of the admin group or not."""
    x = user.groups.filter(name='admin')
    print x
    return x


def special_match(strg, search=re.compile(r'[^A-Za-z0-9., -]').search):
    return not bool(search(strg))


def contact_match(strg, search=re.compile(r'[0-9]\n').search):
    return not bool(search(strg))


def onlyspecchar_match(strg, search=re.compile(r'^[., -]').search):
    return not bool(search(strg))


def onlynumbers(strg, search=re.compile(r'^[0-9]').search):
    return bool(search(strg))
