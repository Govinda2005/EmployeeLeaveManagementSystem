# ELMS/my_flask_app/manager/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from my_flask_app.app import db
from my_flask_app.models import LeaveRequest, User, AuditLog
from my_flask_app.forms import LeaveActionForm
from my_flask_app.decorators import manager_required
from sqlalchemy import or_

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/manage_leaves', methods=['GET', 'POST'])
@login_required
@manager_required # Only managers (or admins) can access
def manage_leaves():
    """
    Displays all leave requests for managers to review, with filtering options.
    """
    # Query all leave requests
    leaves_query = LeaveRequest.query.join(User).order_by(LeaveRequest.request_date.desc())

    # Filtering logic
    status_filter = request.args.get('status')
    employee_filter = request.args.get('employee') # Employee username
    start_date_filter = request.args.get('start_date')
    end_date_filter = request.args.get('end_date')

    if status_filter and status_filter != 'All':
        leaves_query = leaves_query.filter(LeaveRequest.status == status_filter)
    if employee_filter:
        leaves_query = leaves_query.filter(User.username.ilike(f'%{employee_filter}%'))
    if start_date_filter:
        leaves_query = leaves_query.filter(LeaveRequest.start_date >= start_date_filter)
    if end_date_filter:
        leaves_query = leaves_query.filter(LeaveRequest.end_date <= end_date_filter)

    leaves = leaves_query.all()
    
    # Get unique statuses for filter dropdown
    statuses = sorted(list(set([leave.status for leave in LeaveRequest.query.all()])))
    
    return render_template('manage_leaves.html',
                           title='Manage Leave Requests',
                           leaves=leaves,
                           statuses=statuses,
                           selected_status=status_filter,
                           selected_employee=employee_filter,
                           selected_start_date=start_date_filter,
                           selected_end_date=end_date_filter)

@manager_bp.route('/review_leave/<int:leave_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def review_leave(leave_id):
    """Allows managers to review and take action on a specific leave request."""
    leave_request = LeaveRequest.query.get_or_404(leave_id)

    # Managers can only act on Pending requests
    if leave_request.status not in ['Pending']:
        flash(f"Cannot review leave request ID {leave_id} as its status is '{leave_request.status}'.", 'warning')
        return redirect(url_for('manager.manage_leaves'))

    form = LeaveActionForm()
    if form.validate_on_submit():
        leave_request.status = form.status.data
        leave_request.manager_notes = form.manager_notes.data
        db.session.commit()

        audit_action = f"Leave request ID {leave_id} {form.status.data} by manager {current_user.username}"
        audit_log = AuditLog(user_id=current_user.id, action=audit_action,
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash(f'Leave request for {leave_request.applicant.username} has been {form.status.data}.', 'success')
        return redirect(url_for('manager.manage_leaves'))
    elif request.method == 'GET':
        # Pre-fill notes if any, though typically managers start fresh
        form.manager_notes.data = leave_request.manager_notes or ''

    return render_template('review_leave.html',
                           title='Review Leave Request',
                           leave=leave_request,
                           form=form)
