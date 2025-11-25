from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import banking_bp
from .forms import OpenAccountForm, InternalTransferForm, ExternalTransferForm
from ..extensions import db
from ..models import Account, Transaction, User
from ..security import roles_required, log_event
from decimal import Decimal
import random


def generate_account_number():
    while True:
        num = ''.join(str(random.randint(0, 9)) for _ in range(10))
        if not Account.query.filter_by(account_number=num).first():
            return num


@banking_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        accounts = Account.query.filter_by(owner_id=current_user.id).all()
        # last 5 transactions overall
        txs = Transaction.query.filter((Transaction.initiated_by_user_id == current_user.id)).order_by(Transaction.timestamp.desc()).limit(5).all()
        return render_template('banking/dashboard.html', accounts=accounts, transactions=txs)
    return render_template('banking/dashboard.html')


@banking_bp.route('/open-account', methods=['GET', 'POST'])
@login_required
def open_account():
    form = OpenAccountForm()
    if form.validate_on_submit():
        owner = current_user
        # admins could create for others via extra UI (not implemented here)
        acc = Account(account_number=generate_account_number(), owner_id=owner.id, type=form.type.data, balance=form.opening_balance.data, status='active')
        db.session.add(acc)
        db.session.commit()
        log_event('ACCOUNT_CREATED', f'account={acc.account_number} owner={owner.id}')
        flash('Account created', 'success')
        return redirect(url_for('banking.dashboard'))
    return render_template('banking/open_account.html', form=form)


@banking_bp.route('/transfer/internal', methods=['GET', 'POST'])
@login_required
def transfer_internal():
    if current_user.role != 'customer' and current_user.role != 'admin':
        flash('Not allowed', 'danger')
        return redirect(url_for('banking.dashboard'))
    form = InternalTransferForm()
    user_accounts = Account.query.filter_by(owner_id=current_user.id, status='active').all()
    choices = [(a.id, f"{a.account_number} ({a.type}) - {a.balance}") for a in user_accounts]
    form.source_account.choices = choices
    form.target_account.choices = choices
    if form.validate_on_submit():
        src = Account.query.get(form.source_account.data)
        dst = Account.query.get(form.target_account.data)
        amount = Decimal(form.amount.data)
        if not src or not dst:
            flash('Invalid accounts', 'danger')
            return redirect(url_for('banking.transfer_internal'))
        if src.owner_id != current_user.id or dst.owner_id != current_user.id:
            flash('Accounts must belong to you', 'danger')
            return redirect(url_for('banking.transfer_internal'))
        if src.status != 'active' or dst.status != 'active':
            flash('Both accounts must be active', 'danger')
            return redirect(url_for('banking.transfer_internal'))
        if src.balance < amount:
            flash('Insufficient funds', 'danger')
            return redirect(url_for('banking.transfer_internal'))
        # perform transfer inside transaction
        try:
            src.balance = src.balance - amount
            dst.balance = dst.balance + amount
            debit = Transaction(sender_account_id=src.id, receiver_account_id=dst.id, amount=amount, type='debit', description=form.description.data, initiated_by_user_id=current_user.id)
            credit = Transaction(sender_account_id=src.id, receiver_account_id=dst.id, amount=amount, type='credit', description=form.description.data, initiated_by_user_id=current_user.id)
            db.session.add(debit)
            db.session.add(credit)
            db.session.commit()
            log_event('TRANSFER_CREATED', f'from={src.account_number} to={dst.account_number} amount={amount}')
            if amount >= Decimal('10000'):
                log_event('SUSPICIOUS_TRANSFER', f'amount={amount} from={src.account_number}')
            flash('Transfer completed', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Transfer failed', 'danger')
    return render_template('banking/transfer_internal.html', form=form)


@banking_bp.route('/transfer/external', methods=['GET', 'POST'])
@login_required
def transfer_external():
    if current_user.role != 'customer' and current_user.role != 'admin':
        flash('Not allowed', 'danger')
        return redirect(url_for('banking.dashboard'))
    form = ExternalTransferForm()
    user_accounts = Account.query.filter_by(owner_id=current_user.id, status='active').all()
    choices = [(a.id, f"{a.account_number} ({a.type}) - {a.balance}") for a in user_accounts]
    form.source_account.choices = choices
    if form.validate_on_submit():
        src = Account.query.get(form.source_account.data)
        dst = Account.query.filter_by(account_number=form.target_account_number.data.strip()).first()
        amount = Decimal(form.amount.data)
        if not src:
            flash('Invalid source account', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if not dst:
            flash('Target account not found', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if src.owner_id != current_user.id:
            flash('Source account must belong to you', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if src.id == dst.id:
            flash('Cannot transfer to the same account', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if src.status != 'active':
            flash('Source account must be active', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if dst.status != 'active':
            flash('Target account must be active', 'danger')
            return redirect(url_for('banking.transfer_external'))
        if src.balance < amount:
            flash('Insufficient funds', 'danger')
            return redirect(url_for('banking.transfer_external'))
        # perform transfer
        try:
            src.balance = src.balance - amount
            dst.balance = dst.balance + amount
            debit = Transaction(sender_account_id=src.id, receiver_account_id=dst.id, amount=amount, type='debit', description=form.description.data, initiated_by_user_id=current_user.id)
            credit = Transaction(sender_account_id=src.id, receiver_account_id=dst.id, amount=amount, type='credit', description=form.description.data, initiated_by_user_id=current_user.id)
            db.session.add(debit)
            db.session.add(credit)
            db.session.commit()
            log_event('TRANSFER_CREATED', f'from={src.account_number} to={dst.account_number} amount={amount}')
            if amount >= Decimal('10000'):
                log_event('SUSPICIOUS_TRANSFER', f'amount={amount} from={src.account_number}')
            flash('External transfer completed', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Transfer failed', 'danger')
        return redirect(url_for('banking.dashboard'))
    return render_template('banking/transfer_external.html', form=form)


@banking_bp.route('/transactions')
@login_required
def transactions_list():
    if current_user.role == 'customer':
        # transactions for user's accounts
        accounts = [a.id for a in Account.query.filter_by(owner_id=current_user.id).all()]
        txs = Transaction.query.filter((Transaction.sender_account_id.in_(accounts)) | (Transaction.receiver_account_id.in_(accounts))).order_by(Transaction.timestamp.desc()).all()
        return render_template('banking/transactions.html', transactions=txs)
    # admin/auditor view omitted complex filters for brevity
    txs = Transaction.query.order_by(Transaction.timestamp.desc()).limit(200).all()
    return render_template('banking/transactions.html', transactions=txs)
