from flask import (
  Blueprint,
  current_app,
  render_template,
  url_for,
  request,
  redirect,
  flash,
)

from flask_login import login_required, current_user

from config import settings
from lib.util_json import render_json
from snakeeyes.blueprints.billing.forms import SubscriptionForm, \
    UpdateSubscriptionForm, CancelSubscriptionForm, PaymentForm
from snakeeyes.blueprints.billing.models.coupon import Coupon
from snakeeyes.blueprints.billing.models.subscription import Subscription
from snakeeyes.blueprints.billing.models.invoice import Invoice
from snakeeyes.blueprints.billing.decorators import subscription_required, \
    handle_stripe_exceptions

billing = Blueprint('billing', __name__, template_folder='../templates',
                    url_prefix='/subscription')


@billing.route('/pricing')
def pricing():
    if current_user.is_authenticated and current_user.subscription:
        return redirect(url_for('billing.update'))
    
    form = UpdateSubscriptionForm()

    return render_template('billing/pricing.html', form=form,
                            plans=settings.STRIPE_PLANS)


@billing.route('/coupon_code', methods=['POST'])
@login_required
def coupon_code():
    code = request.form.get('coupon_code')
    if code is None:
        return render_json(422, {'error': 'Coupon cannot be processed.'})

    coupon = Coupon.find_by_code(code)
    if coupon is None:
        return render_json(404, {'error': 'Coupon not found.'})

    return render_json(200, {'data': coupon.to_json()})


@billing.route('/create', methods=['GET', 'POST'])
@handle_stripe_exceptions
@login_required
def create():
    if current_user.subscription:
        flash('You already have an active subscription.', 'info')
        return redirect('user.settings')

    plan = request.args.get('plan')
    subscription_plan = Subscription.get_plan_by_id(plan)

    if subscription_plan is None and request.method == 'GET':
        flash('Sorry, that plan does not exist', 'error')
        return redirect(url_for('billing.pricing'))

    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    form = SubscriptionForm(stripe_key=stripe_key, plan=plan)

    if form.validate_on_submit():
        subscription = Subscription()
        created = subscription.create(user=current_user,
                                      name=request.form.get('name'),
                                      plan=request.form.get('plan'),
                                      coupon=request.form.get('coupon_code'),
                                      token=request.form.get('stripe_token'))

        if created:
            flash('Thanks for subscribing.', 'success')
        else:
            flash('You must enable JavaScript for this request', 'warning')
        
        return redirect(url_for('user.settings'))

    return render_template('billing/payment_method.html',
                            form=form, plan=subscription_plan)


# @billing.route('/billing_details')
# @handle_stripe_exceptions
# @login_required
# def billing_details():
#     invoices = Invoice.billing_history(current_user)

#     if current_user.subscription:
#         upcoming = Invoice.upcoming(current_user.payment_id)
#         coupon = Coupon.query \
#             .filter(Coupon.code == current_user.subscription.coupon).first()
#     else:
#         upcoming = None
#         coupon = None

#     return render_template('billing/billing_details.html',
#                            invoices=invoices, upcoming=upcoming, coupon=coupon)


@billing.route('/update', methods=['POST', 'GET'])
@handle_stripe_exceptions
@subscription_required
@login_required
def update():
    currnet_plan = current_user.subscription.plan
    active_plan = Subscription.get_plan_by_id(currnet_plan)
    new_plan = Subscription.get_new_plan(request.form.keys())

    plan = Subscription.get_plan_by_id(new_plan)
    is_same_plan = new_plan == active_plan['id']

    if ((new_plan is not None and plan is None) or is_same_plan) \
        and request.method == 'POST':
        return redirect(url_for('billing.update'))

    form = UpdateSubscriptionForm(coupon_code=current_user.subscription.coupon)

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update(user=current_user,
                                      coupon=request.form.get('coupon_code'),
                                      plan=plan.get('id'))

        if updated:
            flash('Your subscription has been updated.', 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/pricing.html',
                            form=form,
                            plans=settings.STRIPE_PLANS,
                            active_plan=active_plan)

    
@billing.route('/cancel', methods=['GET', 'POST'])
@handle_stripe_exceptions
@login_required
def cancel():
    if not current_user.subscription:
        flash("You don't have an active subscription.", 'error')
        return redirect (url_for('user.settings'))

    form = CancelSubscriptionForm()

    if form.validate_on_submit():
        subscription = Subscription()
        cancelled = subscription.cancel(user=current_user)

        if cancelled:
            flash("Your subscription has been cancelled.", 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/cancel.html', form=form)


@billing.route('/update_payment_method', methods=['GET', 'POST'])
@handle_stripe_exceptions
@login_required
def update_payment_method():
    if not current_user.credit_card:
        flash('You have not added a payment method.', 'error')
        return redirect(url_for('user.settings'))

    active_plan = Subscription.get_plan_by_id(current_user.subscription.plan)
    card = current_user.credit_card

    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    form = SubscriptionForm(stripe_key=stripe_key,
                          plan=active_plan,
                          name=current_user.name)

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update_payment_method(user=current_user,
                                                     credit_card=card,
                                                     name=request.form.get('name'),
                                                     token=request.form.get('stripe_token'))

        if updated:
            flash('Patment method has been updated.', 'success')
        else:
            flash('You need to have JavaScript enabled.', 'warning')

        return redirect(url_for('user.settings'))

    return render_template('billing/payment_method.html', form=form,
                            plam=active_plan, card_last4=str(card.last4))  


@billing.route('/billing_details/page/<int:page>', defaults={'page': 1})
@billing.route('/billing_details/page/<int:page>')
@handle_stripe_exceptions
@login_required
def billing_details(page):
    paginated_invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id) \
            .order_by(Invoice.created_on.desc()).paginate(page, 12, True)

    if current_user.subscription:
        upcoming = Invoice.upcoming(current_user.payment_id)
        coupon = Coupon.query \
            .filter(Coupon.code == current_user.subscription.coupon).first()
    
    else:
        upcoming = None
        coupon = None

    return render_template('billing/billing_details.html',
                             paginated_invoices=paginated_invoices,
                             upcoming=upcoming, coupon=coupon)


@billing.route('/purchase_coins', methods=['GET', 'POST'])
@login_required
def purchase_coins():
    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    form = PaymentForm(stripe_key=stripe_key)

    if form.validate_on_submit():
        coin_bundles = current_app.config.get('COIN_BUNDLES')
        coin_bundles_form = int(request.form.get('coin_bundles'))

        bundle = next((item for item in coin_bundles if
                        item['coins'] == coin_bundles_form), None)

        if bundle is not None:
            invoice = Invoice()
            
            params = {
                'user': current_user,
                'currency': current_app.config.get('STRIPE_CURRENCY'),
                'amount': bundle.get('price_in_cents'),
                'coins': coin_bundles_form,
                'coupon': request.form.get('coupon_code'),
                'token': request.form.get('stripe_token')
            }

            created = invoice.create(**params)

            if created:
                flash(f'{coin_bundles_form} have been added to your account.', 'success')

            else:
                flash('You must enable JavaScript for this request.', 'warning')

            return redirect(url_for('bet.place_bet'))

    return render_template('billing/purchase_coins.html', form=form)