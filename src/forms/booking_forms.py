"""
Booking Forms for Campus Resource Hub.

Forms for creating, managing, and approving bookings.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from datetime import datetime, timedelta


class BookingForm(FlaskForm):
    """Form for creating a new booking."""

    resource_id = HiddenField(
        'Resource ID',
        validators=[DataRequired()]
    )

    start_datetime = DateTimeField(
        'Start Date & Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='Start date and time is required')],
        render_kw={'type': 'datetime-local'}
    )

    end_datetime = DateTimeField(
        'End Date & Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='End date and time is required')],
        render_kw={'type': 'datetime-local'}
    )

    notes = TextAreaField(
        'Booking Notes (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Add any special requests or notes...',
            'rows': 3
        }
    )

    submit = SubmitField('Request Booking')

    def validate_end_datetime(self, field):
        """Ensure end time is after start time."""
        if self.start_datetime.data and field.data:
            if field.data <= self.start_datetime.data:
                raise ValidationError('End time must be after start time')

    def validate_start_datetime(self, field):
        """Ensure booking is not in the past."""
        if field.data and field.data < datetime.now():
            raise ValidationError('Cannot create bookings in the past')

        # Check if booking is too far in the future (e.g., max 6 months)
        if field.data and field.data > datetime.now() + timedelta(days=180):
            raise ValidationError('Cannot create bookings more than 6 months in advance')


class BookingApprovalForm(FlaskForm):
    """Form for approving or rejecting bookings."""

    booking_id = HiddenField(
        'Booking ID',
        validators=[DataRequired()]
    )

    action = SelectField(
        'Action',
        choices=[
            ('approved', 'Approve'),
            ('rejected', 'Reject')
        ],
        validators=[DataRequired(message='Please select an action')]
    )

    comment = TextAreaField(
        'Comment (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Add a comment explaining your decision...',
            'rows': 3
        }
    )

    submit = SubmitField('Submit Decision')


class BookingCancellationForm(FlaskForm):
    """Form for cancelling a booking."""

    booking_id = HiddenField(
        'Booking ID',
        validators=[DataRequired()]
    )

    reason = TextAreaField(
        'Cancellation Reason (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Why are you cancelling this booking?',
            'rows': 3
        }
    )

    submit = SubmitField('Cancel Booking')


class WaitlistForm(FlaskForm):
    """Form for joining waitlist when resource is unavailable."""

    resource_id = HiddenField(
        'Resource ID',
        validators=[DataRequired()]
    )

    desired_start_datetime = DateTimeField(
        'Desired Start Date & Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='Start date and time is required')],
        render_kw={'type': 'datetime-local'}
    )

    desired_end_datetime = DateTimeField(
        'Desired End Date & Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='End date and time is required')],
        render_kw={'type': 'datetime-local'}
    )

    submit = SubmitField('Join Waitlist')

    def validate_desired_end_datetime(self, field):
        """Ensure end time is after start time."""
        if self.desired_start_datetime.data and field.data:
            if field.data <= self.desired_start_datetime.data:
                raise ValidationError('End time must be after start time')
