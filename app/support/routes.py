from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import support_bp
from .forms import SupportTicketForm
from ..extensions import db
from ..models import SupportTicket
from ..security import roles_required, log_event


@support_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = SupportTicketForm()
    if form.validate_on_submit():
        ticket = SupportTicket(customer_id=current_user.id, subject=form.subject.data, description=form.description.data, status='open')
        db.session.add(ticket)
        db.session.commit()
        log_event('TICKET_CREATED', f'ticket_id={ticket.id} customer_id={current_user.id}')
        flash('Support ticket created', 'success')
        return redirect(url_for('support.create_ticket'))
    return render_template('support/create_ticket.html', form=form)


@support_bp.route('/tickets')
@login_required
@roles_required('support', 'admin')
def tickets_list():
    tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    return render_template('support/tickets_list.html', tickets=tickets)
