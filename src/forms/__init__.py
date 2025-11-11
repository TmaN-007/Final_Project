"""
Forms package for Campus Resource Hub.

Contains Flask-WTF forms for:
- Authentication (login, register, password reset)
- Resources (create, edit, search)
- Bookings (create, cancel, approve)
- Reviews (create, edit)
- Messages (send, reply)
"""

from .auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from .resource_forms import ResourceForm, ResourceSearchForm
from .booking_forms import BookingForm, BookingApprovalForm
from .review_forms import ReviewForm

__all__ = [
    'LoginForm',
    'RegisterForm',
    'ForgotPasswordForm',
    'ResetPasswordForm',
    'ResourceForm',
    'ResourceSearchForm',
    'BookingForm',
    'BookingApprovalForm',
    'ReviewForm',
]
