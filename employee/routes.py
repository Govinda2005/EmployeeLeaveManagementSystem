# ELMS/my_flask_app/employee/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from my_flask_app.app import db
from my_flask_app.models import LeaveRequest, AuditLog
from my_flask_app.forms import LeaveApplicationForm
from my_flask_app.decorators import employee_required
from datetime import datetime

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/apply_leave', methods=['GET', 'POST'])
@login_required
@employee_required # Ensure only employees (or higher roles) can apply
def apply_leave():
    """Allows employees to apply for leave."""
    form = LeaveApplicationForm()
    if form.validate_on_submit():
        leave_request = LeaveRequest(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            status='Pending'
        )
        db.session.add(leave_request)
        db.session.commit()

        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Applied for leave: {leave_request.start_date} to {leave_request.end_date}",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash('Your leave request has been submitted!', 'success')
        return redirect(url_for('employee.view_my_leaves'))
    return render_template('apply_leave.html', title='Apply Leave', form=form)

@employee_bp.route('/my_leaves')
@login_required
@employee_required
def view_my_leaves():
    """Displays all leave requests made by the current employee."""
    # Order by request_date descending to show most recent first
    leaves = LeaveRequest.query.filter_by(user_id=current_user.id).order_by(LeaveRequest.request_date.desc()).all()
    return render_template('view_my_leaves.html', title='My Leave Requests', leaves=leaves)

@employee_bp.route('/edit_leave/<int:leave_id>', methods=['GET', 'POST'])
@login_required
@employee_required
def edit_leave(leave_id):
    """Allows an employee to edit a pending leave request."""
    leave_request = LeaveRequest.query.get_or_404(leave_id)

    # Ensure the user owns the leave request and it's still pending
    if leave_request.user_id != current_user.id or leave_request.status != 'Pending':
        abort(403) # Forbidden

    form = LeaveApplicationForm()
    if form.validate_on_submit():
        leave_request.start_date = form.start_date.data
        leave_request.end_date = form.end_date.data
        leave_request.reason = form.reason.data
        db.session.commit()

        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Edited leave request ID {leave_id}: {leave_request.start_date} to {leave_request.end_date}",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash('Your leave request has been updated!', 'success')
        return redirect(url_for('employee.view_my_leaves'))
    elif request.method == 'GET':
        form.start_date.data = leave_request.start_date
        form.end_date.data = leave_request.end_date
        form.reason.data = leave_request.reason
    return render_template('apply_leave.html', title='Edit Leave Request', form=form)

@employee_bp.route('/cancel_leave/<int:leave_id>', methods=['POST'])
@login_required
@employee_required
def cancel_leave(leave_id):
    """Allows an employee to cancel a pending leave request."""
    leave_request = LeaveRequest.query.get_or_404(leave_id)

    # Ensure the user owns the leave request and it's still pending
    if leave_request.user_id != current_user.id or leave_request.status != 'Pending':
        abort(403) # Forbidden

    leave_request.status = 'Cancelled'
    db.session.commit()

    audit_log = AuditLog(user_id=current_user.id,
                         action=f"Cancelled leave request ID {leave_id}: {leave_request.start_date} to {leave_request.end_date}",
                         ip_address=request.remote_addr)
    db.session.add(audit_log)
    db.session.commit()

    flash('Your leave request has been cancelled.', 'info')
    return redirect(url_for('employee.view_my_leaves'))
