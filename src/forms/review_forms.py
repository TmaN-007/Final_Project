"""
Review Forms for Campus Resource Hub.

Forms for creating and managing reviews/ratings.
"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError


class ReviewForm(FlaskForm):
    """Form for creating/editing a review."""

    booking_id = HiddenField(
        'Booking ID',
        validators=[DataRequired()]
    )

    resource_id = HiddenField(
        'Resource ID',
        validators=[DataRequired()]
    )

    rating = IntegerField(
        'Rating',
        validators=[
            DataRequired(message='Rating is required'),
            NumberRange(min=1, max=5, message='Rating must be between 1 and 5')
        ],
        render_kw={'min': '1', 'max': '5', 'step': '1'}
    )

    comment = TextAreaField(
        'Review Comment',
        validators=[
            DataRequired(message='Please write a review comment'),
            Length(min=20, max=1000, message='Review must be between 20 and 1000 characters')
        ],
        render_kw={
            'placeholder': 'Share your experience with this resource...',
            'rows': 5
        }
    )

    submit = SubmitField('Submit Review')

    def validate_comment(self, field):
        """Ensure comment is meaningful (not just repeated characters)."""
        if field.data:
            # Check if comment is mostly repeated characters
            unique_chars = len(set(field.data.replace(' ', '').replace('\n', '')))
            if unique_chars < 5:
                raise ValidationError('Please write a meaningful review')


class HostResponseForm(FlaskForm):
    """Form for resource owners to respond to reviews."""

    review_id = HiddenField(
        'Review ID',
        validators=[DataRequired()]
    )

    host_response = TextAreaField(
        'Your Response',
        validators=[
            DataRequired(message='Response is required'),
            Length(min=10, max=500, message='Response must be between 10 and 500 characters')
        ],
        render_kw={
            'placeholder': 'Respond to this review...',
            'rows': 4
        }
    )

    submit = SubmitField('Post Response')


class ReviewReportForm(FlaskForm):
    """Form for reporting inappropriate reviews."""

    review_id = HiddenField(
        'Review ID',
        validators=[DataRequired()]
    )

    reason = TextAreaField(
        'Report Reason',
        validators=[
            DataRequired(message='Please explain why you are reporting this review'),
            Length(min=10, max=500, message='Reason must be between 10 and 500 characters')
        ],
        render_kw={
            'placeholder': 'Explain why this review should be removed...',
            'rows': 4
        }
    )

    submit = SubmitField('Submit Report')
