from flask import Blueprint, current_app as app, request, session, redirect, url_for, flash

check_users = Blueprint('check_users', __name__)

@check_users.route('/check_field', methods=['GET', 'POST'])
def check_field():
    type = request.args.get('type')
    email = session.get("email", None)
    query = {
        "email": email,
        "reference": {"$exists": True}
    }
    result = app.db_payments['payments'].find_one(query)
    if result:
        return redirect(url_for('routes.result', type=type))
    else:
        app.db_payments['payments'].update_one(
            {"email": email},
            {"$set": {"reference": "PrevUser"}}
        )
        isPrevUser = "True"
        session.pop('email', None)
        session.pop('indexNumber', None)
        
        flash("Due to the new system upgrades your are required to fill in your details again!", "Info")
        return redirect(url_for('routes.base', isPrevUser=isPrevUser))