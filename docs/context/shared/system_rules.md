# Campus Resource Hub - System Rules
**Shared Context for AI Assistants**

## Resource Categories
1. **Study Rooms** - Group study spaces, quiet rooms
2. **AV Equipment** - Projectors, microphones, cameras
3. **Lab Equipment** - Research instruments, specialized tools
4. **Event Spaces** - Auditoriums, conference rooms
5. **Other** - Miscellaneous campus resources

## User Roles and Permissions

### Student
- Can browse and search all published resources
- Can request bookings
- Can send messages to resource owners
- Can leave reviews after completing bookings
- **Cannot** create resources (must request staff role)

### Staff
- All student permissions, plus:
- Can create and manage resources
- Can approve/reject booking requests for their resources
- Can reply to reviews
- Can access resource analytics

### Admin
- All staff permissions, plus:
- Can manage all users (change roles, deactivate)
- Can manage all resources (delete, unpublish)
- Can access system-wide analytics
- Can view audit logs
- Can moderate content

## Booking Rules

1. **Advance Booking:** Must be at least 30 minutes in the future
2. **Maximum Duration:** 8 hours per booking
3. **Overlapping:** Not allowed for same resource
4. **Cancellation:**
   - Users can cancel anytime
   - Cancelled bookings don't block future requests
5. **Approval Workflow:**
   - Pending → Approved/Rejected (by owner)
   - Approved → Can be cancelled
   - Rejected → Cannot be re-approved (must create new request)

## Business Hours
- **Default:** Monday-Friday, 8:00 AM - 10:00 PM
- **Weekends:** Saturday-Sunday, 10:00 AM - 8:00 PM
- Resource owners can set custom hours

## Notification Types
1. **Booking Request** - Sent to resource owner
2. **Booking Approved** - Sent to requester
3. **Booking Rejected** - Sent to requester with reason
4. **Booking Cancelled** - Sent to both parties
5. **Review Submitted** - Sent to resource owner
6. **Admin Action** - Sent to affected user

## Resource Status Values
- **draft** - Not visible to others, editable
- **published** - Visible, bookable
- **archived** - Hidden, not bookable (soft delete)
- **under_review** - Flagged for admin review

## Review Rules
- **Rating:** 1-5 stars (integer only)
- **Eligibility:** Must have completed booking
- **Frequency:** One review per booking
- **Editing:** Reviews can be edited within 24 hours
- **Moderation:** Admins can hide inappropriate reviews

---

**AI Context:**
These rules are referenced by AI assistants when generating recommendations, validating user actions, or explaining system behavior.
