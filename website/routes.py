from flask import Blueprint, request, render_template, current_app as app, session, redirect, url_for, flash, jsonify
from .funcs import CheckGradeRequirements

routes = Blueprint('routes', __name__)

@routes.route('/')
def base():
    session.pop('email', None)
    session.pop('indexNumber', None)
    
    session['isPrevUser'] = request.args.get('isPrevUser')
    return render_template('main-temps/main.html')

@routes.route('/user', methods=['GET', 'POST'])
def redirecting():
    if request.method == 'POST':
        email = request.form.get('email')
        indexNumber = request.form.get('indexNumber')

        session['email'] = email
        session['indexNumber'] = indexNumber
        
        type = request.form.get('type')

        isPrevUser = session["isPrevUser"]
        
        # Properly handle None or empty values
        if indexNumber and indexNumber.strip():
            print(f"User indexNumber is not empty! Its value is {indexNumber} type {type} ||||")
            
            if user_exists(email, indexNumber):
                print(" User exists! ||| ")
                if isPrevUser == "True":
                    if type == "degree":
                        print(f" YOu are regenerating the data for {indexNumber} !!! Type is {type}")
                        return redirect(url_for('routes.generate_data', type=type))
                    else:
                        return redirect(url_for('routes.result', type=type))
                else:
                    return redirect(url_for('check_users.check_field', type=type))
            else:
                print(" User does not exist! Going to payments||| ")

                return redirect(url_for('payments.index', type=type))
        else:
            print("User should be there since indexNumber is empty! ||||")
            if user_exists2(email):
                return redirect(url_for('routes.checkOut'))
            else:
                return redirect(url_for('payments.index', type=type))
        
    return render_template('main-temps/user.html')

def user_exists(email, ksce_index):
    query = {"$or": [{"email": email}, {"ksce_index": ksce_index}]}
    return app.db_payments['payments'].find_one(query) is not None

def user_exists2(email):
    query = {"email": email}
    return app.db_payments['payments'].find_one(query) is not None

@routes.route('/kuccps/', methods=['POST', 'GET'])
def generate_data():
    type = request.args.get('type')
    programmes = []
    
    indexNumber = session.get('indexNumber')
    print(f'You are regenerating the data here!!! of type {degree} Index is {indexNumber}')
    data = []
    try:
        data = list(app.db_payments['data'].find({'index_no': indexNumber }))
    except Exception as e:
        print(f"Exception Error: {e}")

    for datum in data:
        if datum['type'] == type:
            print("You already tried for this one! Please try again.")
            flash("You already tried for this one! Please try again.", "Error")
            return redirect(url_for('routes.base'))
    
    if type == 'diploma':
        programmes = get_diploma()
    elif type == 'degree':
        programmes = get_degree()
    elif type == 'cert':
        programmes = get_cert()
    elif type == 'kmtc':
        programmes = get_kmtc()
    else:
        print(" You were returned!!!!!! ")
        flash("Invalid type specified.", "Error")
        return redirect(url_for('routes.base'))
    
    reference = session.get('reference')
    
    if reference is None:
        reference = "prevUser"
        
    new_data = {
        'refrence': reference,
        'index_no': indexNumber,  # Correct session key
        'type': type,
        'data': programmes,
    }
    # print(f"Database connection: {app.db_payments}")
    
    try:
        print(f"Successfully added data for {session.get('email')} indexNumber {indexNumber} of type {type} |||| ")
        app.db_payments['data'].insert_one(new_data)
        flash("Data saved Successfully!", "Success")
    except Exception as e:
        flash(f'Saving data in the database: {e}', 'Error')
        return redirect(url_for('routes.redirecting'))
    
    return redirect(url_for('routes.result', type=type))


@routes.route('/courses-result', methods=['POST', 'GET'])
def result():
    indexNumber = session.get('indexNumber')
    type = request.args.get('type')
    
    query = {"index_no": indexNumber}
    data = list(app.db_payments['data'].find(query, {"_id": False}))
    
    if not data:
        flash("Sorry, it seems there is an issue with the data you uploaded. Check your index number and try again. You can contact 0799196459.", category="Error")
        return redirect(url_for("routes.base"))
        
    result = []
    
    for datum in data:
        stored_type = datum.get('type')
        if stored_type == type:
            result = datum['data']
            break
        
        if stored_type == None:
            print(" It seems you are an earlier user. ")
            return redirect(url_for('routes.var'))
    
    if result == [] :
        flash(" It seems you don't have data for this category! Go back and try again", "Error")
    else:
        flash("Data retrieved Successfully!", "Success")
        
    if type:
        type = type.capitalize()  # Capitalize the first letter if type is not None
    
    
    
    print(f"The number of categories for {session.get('indexNumber')} of {session.get('email')} is {len(data)} ||||| |")
    
    template = 'acc-temps/data2.html' if type in ["Diploma", "Cert", "kmtc"] else 'acc-temps/data.html'
    
    return render_template(template, programmes=result, email=session.get('email'), index_no=indexNumber, type=type)

@routes.route('/var', methods=['GET', 'POST'])
def var():
    if request.method == 'POST':
        previous_type = request.form.get('type')
        indexNumber = session.get('indexNumber')
        query = {"index_no": indexNumber}

        # Use $set to update the field, even if the document already exists
        new_field = {"type": previous_type}

        # Update the document with the specified index number and set the type field
        result = app.db_payments['data'].update_one(
            query,
            {
                '$set': new_field
            },
            upsert=True  # This will create the document if it doesn't exist
        )

        # Check if the document was updated or inserted
        if result.upserted_id is not None:
            print('New document inserted Successfully.')
        elif result.matched_count > 0:
            print('Document updated Successfully.')
            print(f" Result {result}")
        else:
            print('No document found with the specified index number.')

        return redirect(url_for('routes.result', type=previous_type))

    else:
        return render_template('main-temps/newcopy.html')


@routes.route('/check-out', methods=['GET', 'POST'])
def checkOut():
    if request.method == 'POST':
        previous_type = request.form.get('type')
        
        indexNumber = session.get('indexNumber')
        query = {"index_no": indexNumber}
        
        new_field = {"type": previous_type}
        
        # Update the document with the specified index number
        result = app.db_payments['data'].update_one(
            query,
            {
                '$setOnInsert': new_field
            },
            upsert=True  # This will create the document if it doesn't exist
        )
        
        # Check if the document was updated or inserted
        if result.upserted_id is not None:
            print('New document inserted Successfully.')
        elif result.matched_count > 0:
            print('Document already exists with the specified field.')
        else:
           print('No document found with the specified index number.')
        
        return redirect(url_for('newer.home'))
                
    else:
        return render_template('main-temps/newcopy.html',)


# -------------------- THESE ARE THE FUNCTIONS THAT GENERATE THE KMTC DATA --------------------------
def get_kmtc():
    print(" You are in the kmtc DOM ")
    subject_clusters = session.get('subjects_clusters')

    if subject_clusters is None:
        print(" There is an isssue!! ")
        raise ValueError("subject_clusters is None ?>>>")
    
    qualified_programmes = []

    min_grade, grades = get_grade_minimum(subject_clusters)

    doc_name = "kmtc"

    data = list(app.dp_courses[doc_name].find({}, {"_id": False}))

    for doc in data:
        if 'minimum_subject_requirements' not in doc or doc['minimum_subject_requirements'] is None:
            doc['minimum_subject_requirements'] = {}

    grade_check_obj = CheckGradeRequirements()
    grade_check_obj.programmes = data
    grade_check_obj.users = grades

    min_grade_result = get_diploma_minimum(min_grade, grade_check_obj.programmes)

    if min_grade_result != []:
        grade_check_obj.programmes = min_grade_result
        q_programmes = grade_check_obj.top_view()
        qualified_programmes.append({"cluster_name": doc_name, "programme": q_programmes})

    return qualified_programmes

# The rest of your functions remain unchanged, but consider refactoring similar functions as mentioned above.
# -------------------- THESE ARE THE FUNCTIONS THAT GENERATE THE CERT DATA --------------------------
def get_cert():
    print(" You are in the cert DOM ")
    subject_clusters = session.get('subjects_clusters')

    if subject_clusters is None:
        print(" There is an isssue!! ")
        raise ValueError("subject_clusters is None ?>>>")

    
    diploma_programes = [
        {'name': "Agricultural_Sciences_Related", 'no': "1"},
        {'name': "Animal_Health_Related", 'no': "2"},
        {'name': "Applied_Sciences", 'no': "3"},
        {'name': "Building_Construction_Related", 'no': "4"},
        {'name': "Business_Related", 'no': "5"},
        {'name': "Clothing_Fashion_Textile", 'no': "6"},
        {'name': "Computing_IT_Related", 'no': "7"},
        {'name': "Engineering_Cert_Related", 'no': "8"}, 
        {'name': "Engineering_Technology_Related", 'no': "9"},
        {'name': "Environmental_Sciences", 'no': "10"},
        {'name': "Food_Science_Related", 'no': "11"},
        {'name': "Graphics_MediaStudies_Related", 'no': "12"},
        {'name': "Health_Sciences_Related", 'no': "13"},
        {'name': "Hospitality_Hotel_Tourism_Related", 'no': "14"},
        {'name': "Library_Information_Science", 'no': "15"},
        {'name': "HairDressing_Beauty_Therapy", 'no': "16"},
        {'name': "Natural_Sciences_Related", 'no': "17"},
        {'name': "Nutrition_Dietetics", 'no': "18"},
        {'name': "Social_Sciences", 'no': "19"},
        {'name': "Tax_Custom_Administration", 'no': "20"},
        {'name': "clothing", 'no': "21"},
    ]

    qualified_programmes = []

    min_grade, grades = get_grade_minimum(subject_clusters)

    for documents in diploma_programes:
        doc_name = documents.get('name')
        doc_no = documents.get('no')

        data = list(app.cert_courses[doc_name].find({}, {"_id": False}))

        for doc in data:
            if 'minimum_subject_requirements' not in doc or doc['minimum_subject_requirements'] is None:
                doc['minimum_subject_requirements'] = {}

        grade_check_obj = CheckGradeRequirements()
        grade_check_obj.programmes = data
        grade_check_obj.users = grades

        min_grade_result = get_diploma_minimum(min_grade, grade_check_obj.programmes)

        if min_grade_result != []:
            grade_check_obj.programmes = min_grade_result
            q_programmes = grade_check_obj.top_view()
            qualified_programmes.append({"cluster_name": doc_name, "programme": q_programmes})

    return qualified_programmes



# -------------------- THESE ARE THE FUNCTIONS THAT GENERATE THE DIPLOMA DATA --------------------------

@routes.route('/diploma', methods=['POST', 'GET'])
def diploma():
    if request.method == 'POST':
        subjects = request.form.to_dict()
        
        subjects_clusters = []
        for key, value in subjects.items():
            if value:
                subjects_clusters.append({key: value})
                # print(f"{key}-{value}")
                
        # print(f" >>>> This is how the user's data looks like: {subjects_clusters} <<<<< ")
        session['subjects_clusters'] = subjects_clusters
                
        return redirect(url_for('routes.redirecting'))
    else:
        return render_template('acc-temps/index2.html')
    

def get_diploma():
    subject_clusters = session.get('subjects_clusters')

    diploma_programes = [
        {'name': "Agricultural_Sciences_Related", 'no': "1"},
        {'name': "Animal_Health_Related", 'no': "2"},
        {'name': "Applied_Sciences", 'no': "3"},
        {'name': "Building_Construction_Related", 'no': "4"},
        {'name': "Business_Related", 'no': "5"},
        {'name': "Clothing_Fashion_Textile", 'no': "6"},
        {'name': "Computing_IT_Related", 'no': "7"},
        {'name': "Education_Related", 'no': "8"},
        {'name': "Engineering_Technology_Related", 'no': "9"},
        {'name': "Environmental_Sciences", 'no': "10"},
        {'name': "Food_Science_Related", 'no': "11"},
        {'name': "Graphics_MediaStudies_Related", 'no': "12"},
        {'name': "Health_Sciences_Related", 'no': "13"},
        {'name': "Hospitality_Hotel_Tourism_Related", 'no': "14"},
        {'name': "Library_Information_Science", 'no': "15"},
        {'name': "Music_Related", 'no': "16"},
        {'name': "Natural_Sciences_Related", 'no': "17"},
        {'name': "Nutrition_Dietetics", 'no': "18"},
        {'name': "Social_Sciences", 'no': "19"},
        {'name': "Tax_Custom_Administration", 'no': "20"},
        {'name': "Technical_Courses", 'no': "20"},
    ]

    qualified_programmes = []

    min_grade, grades = get_grade_minimum(subject_clusters)

    for documents in diploma_programes:
        doc_name = documents.get('name')
        doc_no = documents.get('no')

        data = list(app.dp_courses[doc_name].find({}, {"_id": False}))

        # print(f"\n >><> You have {len(data)} in your collection number {doc_no} {doc_name} <><<\n")
        for doc in data:
            if 'minimum_subject_requirements' not in doc or doc['minimum_subject_requirements'] is None:
                doc['minimum_subject_requirements'] = {}

        # print(" Done")
        grade_check_obj = CheckGradeRequirements()

        grade_check_obj.programmes = data
        grade_check_obj.users = grades

        # CHECKING THE minimum grade required

        min_grade_result = get_diploma_minimum(min_grade, grade_check_obj.programmes)

        if min_grade_result != []:

            grade_check_obj.programmes = min_grade_result

            q_programmes = grade_check_obj.top_view()

            qualified_programmes.append({"cluster_name": doc_name, "programme":q_programmes})

    # print(f" Total length of returned docs are {len(qualified_programmes)} and they are {qualified_programmes} )")    
    return qualified_programmes

def get_diploma_minimum(min_grade, programmes):

    result = []

    grades = {
        "A": 12,
        "A-": 11,
        "B+": 10,
        "B": 9,
        "B-": 8,
        "C+": 7,
        "C": 6,
        "C-": 5,
        "D+": 4,
        "D": 3,
        "D-": 2,
        "E": 1,
    }

    for program in programmes:
        main_min_grade = program.get('minimum_grade', None)

        # print(f" THESE IS THE MINIMUM GRADE REQUIRED {main_min_grade} |||| |")
        if main_min_grade is None or main_min_grade == "" or main_min_grade == "null":
            # print(" Min grade is None thus you Qualify!")
            result.append(program)

        for key, value in main_min_grade.items(): 
            if grades.get(min_grade, 0) >= grades.get(value, 0):
                # print(" Qualified for the minimum grade requirement for this programs ")
                result.append(program)     

    return result

def get_grade_minimum(subject_cluster):

    min_grade = ""

    grades = []

    for weights in subject_cluster:
        for key, value in weights.items():
            if key.startswith('overall'):
                min_grade = value
            else:
                grades.append({key: value})

    return min_grade, grades
    
    
# ------------------ THESE ARE THE FUNCTIONS THAT GENERATE THE DEGREE DATA ----------------------------
@routes.route('/degree', methods=['POST', 'GET'])
def degree():
    if request.method == 'POST':
        subjects = request.form.to_dict()
    
        subjects_clusters = []
        for key, value in subjects.items():
            if value:
                subjects_clusters.append({key: value})
                # print(f"{key}-{value}")
                
        # print(f" >>>> This is how the user's data looks like: {subjects_clusters} <<<<< ")
        session['subjects_clusters'] = subjects_clusters
        
        return redirect(url_for('routes.redirecting'))
    else:
        return render_template('acc-temps/index.html')
    

def get_degree():
    
    subject_clusters = session.get('subjects_clusters')

    degree_programes = [
        {'name': "cluster_1", 'no': "1"},
        {'name': "cluster_2", 'no': "2"},
        {'name': "cluster_3", 'no': "3"},
        {'name': "cluster_4", 'no': "4"},
        {'name': "cluster_5", 'no': "5"},
        {'name': "cluster_6", 'no': "6"},
        {'name': "cluster_7", 'no': "7"},
        {'name': "cluster_8", 'no': "8"},
        {'name': "cluster_9", 'no': "9"},
        {'name': "cluster_10", 'no': "10"},
        {'name': "cluster_11", 'no': "11"},
        {'name': "cluster_12", 'no': "12"},
        {'name': "cluster_13", 'no': "13"},
        {'name': "cluster_14", 'no': "14"},
        {'name': "cluster_15", 'no': "15"},
        {'name': "cluster_16", 'no': "16"},
        {'name': "cluster_17", 'no': "17"},
        {'name': "cluster_18", 'no': "18"},
        {'name': "cluster_19", 'no': "19"},
        {'name': "cluster_20", 'no': "20"}
    ]

    qualified_programmes = []

    cluster_weights, grades = get_cluster_and_subs(subject_clusters)

    for documents in degree_programes:
        doc_name = documents.get('name')
        doc_no = documents.get('no')

        data = list(app.db[doc_name].find({}, {"_id": False}))

        # print(f"\n >><> You have {len(data)} in your collection number {doc_no} {doc_name} <><<\n")
        for doc in data:
            if 'minimum_subject_requirements' not in doc or doc['minimum_subject_requirements'] is None:
                doc['minimum_subject_requirements'] = {}

        # print(" Done")
        grade_check_obj = CheckGradeRequirements()

        grade_check_obj.programmes = data
        grade_check_obj.users = grades

        # CHECKING THE CLUSTER WEIGHT 
        users_weight = get_users_cluster(cluster_weights, doc_no)

        cut_off_result = compare_cluster(users_weight, grade_check_obj.programmes)

        if cut_off_result != []:

            grade_check_obj.programmes = cut_off_result

            q_programmes = grade_check_obj.top_view()

            qualified_programmes.append({"cluster_name": doc_name, "programme":q_programmes})

    # print(f" Total length of returned docs are {len(qualified_programmes)} and they are {qualified_programmes} )")    
    return qualified_programmes

def get_cluster_and_subs(subject_cluster):

    grades = []

    cluster_weights = []

    for weights in subject_cluster:
        for key, value in weights.items():
            if key.startswith('cl'):
                cluster_weights.append({key: value})
            else:
                grades.append({key: value})

    return cluster_weights, grades

def get_users_cluster(cluster_list, cluster_no):
    for weight in cluster_list:
        for key, value in weight.items():
            if key.endswith(cluster_no):
                return value

def compare_cluster(users_weight, cluster_docs_data):
    result = []

    users_weight = float(users_weight)

    for doc in cluster_docs_data:
        cut_off_point = doc.get('cut_off_points', None)
        
        # Handle cases where cut_off_point is a list
        if isinstance(cut_off_point, list):
            # Take the first element of the list, or default to None if the list is empty
            cut_off_point = cut_off_point[0] if cut_off_point else None

        if cut_off_point is None or cut_off_point == "":
            # print(" Cut of points is None thus you Qualify!")
            result.append(doc)
            continue
        else:
            try:
                cut_off_point = float(cut_off_point)

                if users_weight <= 0.000:
                    # print(f" You have a cluster weight of zero Thus you dont qualify in any of this cluster's docs.")
                    break           
                elif users_weight >= cut_off_point:
                    # print(" You qualify!")
                    result.append(doc)
                else:
                    # print(f" You do not qualify! Cut off needed {cut_off_point} You got {users_weight}")
                    pass
            except ValueError as err:
                # print(f" Value Error: {err} in db so you Qualify!")
                result.append(doc)

    return result