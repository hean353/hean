from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app as app
from datetime import datetime

payments = Blueprint('payments', __name__)

AMOUNT = 199000
AMOUNT_TWO = 10000

@payments.route('/', methods=['GET', 'POST'])
def index():
    try:
        email = session.get('email')
        ksce_index = session.get('indexNumber')
        type = request.args.get('type')
        subs = session.get('subjects_clusters')
        if not subs:
            session.pop('email', None)
            session.pop('indexNumber', None)
            
            flash("You did not enter your grades!", "Error")
            return redirect(url_for('routes.base'))
        else:
            return render_template('main-temps/paystack.html', email=email, ksce_index=ksce_index, type=type)
    except Exception as e:
        flash(f"An Error occurred: {e}", "Error")
        return redirect(url_for('routes.base'))

@payments.route('/verify-payment', methods=['GET', 'POST'])
def verify_payment():
    try:
        data = request.get_json() if request.method == 'POST' else None
        reference = data.get('reference') if data else request.args.get('reference')
        type = data.get('type') if data else request.args.get('type')
        email = session.get('email')
        ksce_index = session.get('indexNumber')

        if reference:
            if user_exists(email, ksce_index):
                print("User already exists!")
            else:
                create_user(email, ksce_index, reference)
            session['reference'] = reference
            return redirect(url_for('routes.generate_data', type=type))
        else:
            flash("Failed to complete payment. Please try again.", "Error")
            return redirect(url_for('payments.index', type=type))
    except Exception as e:
        flash(f"An Error occurred: {e}", "Error")
        return redirect(url_for('payments.index', type=type))

def create_user(email, ksce_index, reference):
    user = {
        'email': email,
        'ksce_index': ksce_index,
        'status': 'success',
        'reference': reference,
        'timestamp': datetime.utcnow()
    }
    app.db_payments['payments'].insert_one(user)

def user_exists(email, ksce_index):
    query = {"$or": [{"email": email}, {"ksce_index": ksce_index}]}
    return app.db_payments['payments'].find_one(query) is not None