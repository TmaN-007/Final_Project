"""
Message Controller for Campus Resource Hub.

Handles messaging between users, thread management, and automated notifications.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from src.data_access.message_dal import MessageDAL
from src.data_access.user_dal import UserDAL
from src.models.message import MessageThread, Message

# Create blueprint
message_bp = Blueprint('message', __name__, url_prefix='/messages')


@message_bp.route('/')
@message_bp.route('/thread/<int:thread_id>')
@login_required
def inbox(thread_id=None):
    """
    Display user's message inbox with all threads.
    Split-screen layout with thread list and active conversation.
    """
    # Get all threads for current user
    threads = MessageDAL.get_threads_by_user(current_user.user_id)

    # Convert to MessageThread objects
    thread_objects = [MessageThread(thread) for thread in threads]

    # Get active thread data
    active_thread = None
    messages = []
    participants = []

    if thread_id:
        # Load specified thread
        thread_data = MessageDAL.get_thread_by_id(thread_id)
        if thread_data:
            active_thread = MessageThread(thread_data)
            participants = MessageDAL.get_thread_participants(thread_id)
            participant_ids = [p['user_id'] for p in participants]

            if current_user.user_id in participant_ids:
                messages_data = MessageDAL.get_messages_in_thread(thread_id)
                messages = [Message(msg) for msg in messages_data]
                MessageDAL.mark_thread_as_read(thread_id, current_user.user_id)
                participants = [p for p in participants if p['user_id'] != current_user.user_id]
    # Don't auto-open any thread - user must click on a thread to view it

    return render_template(
        'messages/inbox.html',
        threads=thread_objects,
        active_thread=active_thread,
        messages=messages,
        participants=participants
    )


@message_bp.route('/thread/<int:thread_id>')
@login_required
def thread(thread_id):
    """
    Display a specific message thread with all messages.
    Similar to iMessage conversation view.
    """
    # Get thread details
    thread_data = MessageDAL.get_thread_by_id(thread_id)

    if not thread_data:
        flash('Thread not found.', 'error')
        return redirect(url_for('message.inbox'))

    thread_obj = MessageThread(thread_data)

    # Verify user is participant in thread
    participants = MessageDAL.get_thread_participants(thread_id)
    participant_ids = [p['user_id'] for p in participants]

    if current_user.user_id not in participant_ids:
        flash('You do not have access to this thread.', 'error')
        return redirect(url_for('message.inbox'))

    # Get all messages in thread
    messages = MessageDAL.get_messages_in_thread(thread_id)
    message_objects = [Message(msg) for msg in messages]

    # Mark messages as read
    MessageDAL.mark_thread_as_read(thread_id, current_user.user_id)

    # Get other participants' info
    other_participants = [p for p in participants if p['user_id'] != current_user.user_id]

    return render_template(
        'messages/thread.html',
        thread=thread_obj,
        messages=message_objects,
        participants=other_participants
    )


@message_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send a new message in a thread.
    Supports both form submission and AJAX requests.
    """
    thread_id = request.form.get('thread_id')
    content = request.form.get('content', '').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not content:
        if is_ajax:
            return jsonify({'success': False, 'error': 'Message cannot be empty.'}), 400
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('message.inbox', thread_id=thread_id))

    if len(content) > 2000:
        if is_ajax:
            return jsonify({'success': False, 'error': 'Message is too long. Maximum 2000 characters.'}), 400
        flash('Message is too long. Maximum 2000 characters.', 'error')
        return redirect(url_for('message.inbox', thread_id=thread_id))

    # Verify user is participant in thread
    participants = MessageDAL.get_thread_participants(thread_id)
    participant_ids = [p['user_id'] for p in participants]

    if current_user.user_id not in participant_ids:
        if is_ajax:
            return jsonify({'success': False, 'error': 'You do not have access to this thread.'}), 403
        flash('You do not have access to this thread.', 'error')
        return redirect(url_for('message.inbox'))

    # Determine receiver (the other participant in the thread)
    receiver_id = None
    for p in participants:
        if p['user_id'] != current_user.user_id:
            receiver_id = p['user_id']
            break

    if not receiver_id:
        if is_ajax:
            return jsonify({'success': False, 'error': 'Could not find message recipient.'}), 400
        flash('Could not find message recipient.', 'error')
        return redirect(url_for('message.inbox'))

    # Send message
    message_id = MessageDAL.send_message(
        thread_id=thread_id,
        sender_id=current_user.user_id,
        receiver_id=receiver_id,
        content=content
    )

    if message_id:
        if is_ajax:
            # Get the sent message details
            from src.models.message import Message
            from datetime import datetime
            return jsonify({
                'success': True,
                'message': {
                    'message_id': message_id,
                    'content': content,
                    'sender_id': current_user.user_id,
                    'sent_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        flash('Message sent successfully.', 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'error': 'Failed to send message.'}), 500
        flash('Failed to send message.', 'error')

    return redirect(url_for('message.inbox', thread_id=thread_id))


@message_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    """
    Create a new message thread.
    """
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id', type=int)
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content', '').strip()
        resource_id = request.form.get('resource_id', type=int)

        if not recipient_id:
            flash('Please select a recipient.', 'error')
            return redirect(url_for('message.new_thread'))

        if not content:
            flash('Message content is required.', 'error')
            return redirect(url_for('message.new_thread'))

        # Create thread
        thread_id = MessageDAL.create_thread(
            subject=subject,
            resource_id=resource_id
        )

        if not thread_id:
            flash('Failed to create thread.', 'error')
            return redirect(url_for('message.inbox'))

        # Add participants
        MessageDAL.add_thread_participant(thread_id, current_user.user_id)
        MessageDAL.add_thread_participant(thread_id, recipient_id)

        # Send first message
        MessageDAL.send_message(
            thread_id=thread_id,
            sender_id=current_user.user_id,
            receiver_id=recipient_id,
            content=content
        )

        flash('Message sent successfully.', 'success')
        return redirect(url_for('message.thread', thread_id=thread_id))

    # GET request - show form
    # Get recipient from query params (e.g., from resource page)
    recipient_id = request.args.get('recipient_id', type=int)
    resource_id = request.args.get('resource_id', type=int)

    # Check if thread already exists between these users for this resource
    if recipient_id and resource_id:
        existing_thread_id = MessageDAL.find_existing_thread(
            user_id=current_user.user_id,
            other_user_id=recipient_id,
            resource_id=resource_id
        )
        if existing_thread_id:
            # Redirect to existing thread
            return redirect(url_for('message.thread', thread_id=existing_thread_id))

    # Load recipient if specified
    recipient = None
    if recipient_id:
        recipient_data = UserDAL.get_user_by_id(recipient_id)
        if recipient_data:
            from src.models.user import User
            recipient = User(recipient_data)

    # Load resource if specified
    resource = None
    if resource_id:
        from src.data_access.resource_dal import ResourceDAL
        resource_data = ResourceDAL.get_resource_by_id(resource_id)
        if resource_data:
            from src.models.resource import Resource
            resource = Resource(resource_data)

    # Load all users for recipient dropdown (if no specific recipient)
    users = []
    if not recipient:
        all_users = UserDAL.get_all_users()
        from src.models.user import User
        users = [User(u) for u in all_users if u['user_id'] != current_user.user_id]

    return render_template(
        'messages/new_thread.html',
        recipient=recipient,
        recipient_id=recipient_id,
        resource=resource,
        resource_id=resource_id,
        users=users
    )


@message_bp.route('/api/threads')
@login_required
def api_threads():
    """
    API endpoint to get user's threads (for live updates).
    """
    threads = MessageDAL.get_threads_by_user(current_user.user_id)

    return jsonify({
        'threads': [{
            'thread_id': t['thread_id'],
            'subject': t.get('subject'),
            'resource_title': t.get('resource_title'),
            'last_message_at': t.get('last_message_at'),
            'unread_count': t.get('unread_count', 0)
        } for t in threads]
    })


@message_bp.route('/api/unread_count')
@login_required
def api_unread_count():
    """
    API endpoint to get total unread message count for current user.
    Used for auto-updating notification badge.
    Optionally excludes a specific thread (e.g., the currently active thread).
    """
    exclude_thread_id = request.args.get('exclude_thread_id', type=int)

    threads = MessageDAL.get_threads_by_user(current_user.user_id)
    total_unread = sum(
        t.get('unread_count', 0)
        for t in threads
        if not exclude_thread_id or t['thread_id'] != exclude_thread_id
    )

    return jsonify({
        'unread_count': total_unread
    })


@message_bp.route('/api/thread/<int:thread_id>/messages')
@login_required
def api_messages(thread_id):
    """
    API endpoint to get messages in a thread (for live updates).
    """
    # Verify user is participant
    participants = MessageDAL.get_thread_participants(thread_id)
    participant_ids = [p['user_id'] for p in participants]

    if current_user.user_id not in participant_ids:
        return jsonify({'error': 'Access denied'}), 403

    messages = MessageDAL.get_messages_in_thread(thread_id)

    return jsonify({
        'messages': [{
            'message_id': m['message_id'],
            'sender_id': m['sender_id'],
            'sender_name': m.get('sender_name'),
            'content': m['content'],
            'sent_at': m['sent_at'],
            'is_system': m.get('is_system', False)
        } for m in messages]
    })
