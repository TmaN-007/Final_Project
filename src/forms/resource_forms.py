"""
Resource Forms for Campus Resource Hub.

Forms for creating, editing, and searching resources.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError


class ResourceForm(FlaskForm):
    """Form for creating/editing resources."""

    title = StringField(
        'Resource Title',
        validators=[
            DataRequired(message='Title is required'),
            Length(min=5, max=200, message='Title must be between 5 and 200 characters')
        ],
        render_kw={'placeholder': 'e.g., Study Room 201 - Kelley School'}
    )

    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message='Description is required'),
            Length(min=20, max=2000, message='Description must be between 20 and 2000 characters')
        ],
        render_kw={
            'placeholder': 'Describe your resource in detail...',
            'rows': 6
        }
    )

    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[DataRequired(message='Category is required')],
        choices=[]  # Will be populated dynamically from database
    )

    location = StringField(
        'Location',
        validators=[
            DataRequired(message='Location is required'),
            Length(max=200)
        ],
        render_kw={'placeholder': 'e.g., Kelley School, Room 201'}
    )

    capacity = IntegerField(
        'Capacity',
        validators=[
            Optional(),
            NumberRange(min=1, max=1000, message='Capacity must be between 1 and 1000')
        ],
        render_kw={'placeholder': 'Leave empty for single-item resources'}
    )

    availability_mode = SelectField(
        'Availability Mode',
        choices=[
            ('rules', 'Based on Availability Rules'),
            ('open', 'Always Open (No Booking Required)'),
            ('by-request', 'By Request Only')
        ],
        default='rules',
        validators=[DataRequired()]
    )

    requires_approval = BooleanField(
        'Requires Approval',
        default=False,
        description='Check if bookings need owner approval'
    )

    status = SelectField(
        'Status',
        choices=[
            ('draft', 'Draft (Not Published)'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='draft',
        validators=[DataRequired()]
    )

    # Image upload fields
    primary_image = FileField(
        'Primary Image',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG, JPEG, and PNG images allowed')
        ]
    )

    additional_images = FileField(
        'Additional Images (Optional)',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG, JPEG, and PNG images allowed')
        ]
    )

    submit = SubmitField('Save Resource')

    def validate_capacity(self, field):
        """Ensure capacity is positive if provided."""
        if field.data is not None and field.data < 1:
            raise ValidationError('Capacity must be at least 1')


class ResourceSearchForm(FlaskForm):
    """Form for searching and filtering resources."""

    query = StringField(
        'Search',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'Search resources...'}
    )

    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[Optional()],
        choices=[],  # Populated dynamically
        default=''
    )

    location = StringField(
        'Location',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'Filter by location...'}
    )

    min_capacity = IntegerField(
        'Minimum Capacity',
        validators=[Optional(), NumberRange(min=1)]
    )

    availability_mode = SelectField(
        'Availability',
        choices=[
            ('', 'All'),
            ('rules', 'Bookable'),
            ('open', 'Open Access'),
            ('by-request', 'By Request')
        ],
        default='',
        validators=[Optional()]
    )

    sort_by = SelectField(
        'Sort By',
        choices=[
            ('created_desc', 'Newest First'),
            ('created_asc', 'Oldest First'),
            ('title_asc', 'Title (A-Z)'),
            ('title_desc', 'Title (Z-A)'),
            ('rating_desc', 'Highest Rated'),
            ('capacity_desc', 'Largest Capacity')
        ],
        default='created_desc',
        validators=[Optional()]
    )

    submit = SubmitField('Search')
