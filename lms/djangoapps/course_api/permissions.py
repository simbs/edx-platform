"""
Course API Authorization functions
"""

from student.roles import GlobalStaff


def can_view_courses_for_username(requesting_user, target_username):
    """
    Determine whether `requesting_user` has permission to view courses available
    to the user identified by `target_username`.  All users can view courses
    available to themselves.  Staff users can view courses available to any given
    user.

    Arguments:
        requesting_user (User): The user requesting permission to view another

        target_username (string):
            The name of the user `requesting_user` would like
            to access.

    Return value:
        Boolean:
            `True` if `requesting_user` is authorized to view courses as
            `target_username`.  Otherwise, `False`
    """
    if not target_username:
        # target_username cannot be None
        return False
    elif requesting_user.username == target_username:
        # all users can view their own courses
        return True
    else:
        # staff users can view any other user's courses
        staff = GlobalStaff()
        return staff.has_user(requesting_user)
