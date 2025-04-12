from flask import Blueprint, render_template, redirect, url_for, current_app, request, flash, session

newer = Blueprint('newer', __name__)

@newer.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            email = session.get('email')
            user_details = current_app.db_payments['payments'].find_one({"email": email})
            if user_details:
                user_index = user_details.get('ksce_index', "")
                session['indexNumber'] = user_index
                type = request.form.get('type')
                user_data = list(current_app.db_payments['data'].find({"index_no": user_index}))
                for datum in user_data:
                    if type == datum.get('type'):
                        flash(f"You already tried for this category! Please choose another one", "error")
                        return redirect(url_for('newer.home'))
                if session.get('subjects_clusters') is None:
                    flash("You did not enter your grades!", "error")
                    return redirect(url_for('routes.base'))
                subs = session.get('subjects_clusters')
                if not subs:
                    session.clear()
                    flash("You did not enter your grades!", "error")
                    return redirect(url_for('routes.base'))
                else:
                    return render_template('main-temps/paystack2.html', email=email, ksce_index=user_index, type=type)
            else:
                flash("User details not found!", "error")
                return redirect(url_for('newer.home'))
        else:
            return render_template('main-temps/new.html')
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('newer.home'))
