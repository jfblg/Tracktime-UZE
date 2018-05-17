import os
from src.config import UPLOAD_FOLDER_NAME
from src.common.utils import time_funcs
from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from src.models.participants.participants import ParticipantModel, RunnerRegistrationForm
from src.models.startlist.startlist import StartlistModel, StartlistNameModel
from src.models.categories.categories import CategoryModel
from src.models.participants.mass_import_xls import MassImport
from werkzeug.utils import secure_filename

# Not all imports from above are actually used.
# They are listed for your reference.

participants_blueprint = Blueprint("participants", __name__)

UPLOAD_FOLDER = '/path/to/the/uploads'


@participants_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    form = RunnerRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        gender = request.form['gender']
        year = request.form['year'].strip()

        runner = ParticipantModel(first_name=first_name.title(),
                                  last_name=last_name.title(),
                                  gender=gender.lower(),
                                  year=year, )
        runner.save_to_db()
        return render_template('participants/signup_success.html',
                               first_name=runner.first_name,
                               last_name=runner.last_name,
                               gender=runner.gender,
                               year=runner.year,
                               form=form)

    return render_template('participants/signup.html', form=form)


@participants_blueprint.route('/show_all_for_edit', methods=['GET', 'POST'])
def show_all_for_edit():
    # get ordered participants
    return render_template('participants/participants_edit_menu.html',
                           data=ParticipantModel.get_participants_ordered())


@participants_blueprint.route('/show_one_selected', methods=['POST'])
def show_one_selected():
    # show details of a selected participant
    # get id of selected athlete from post form
    # show his details
    participant_id = request.form['participant_select']
    participant = ParticipantModel.get_by_id(participant_id)

    # save category_id to session for the function edit_selected_category
    session['participant_id_to_edit'] = participant_id

    return render_template('participants/participants_edit_selected.html',
                           last_name=participant.last_name,
                           first_name=participant.first_name,
                           gender=participant.gender,
                           year=participant.year)


@participants_blueprint.route('/edit_one_selected', methods=['POST'])
def edit_one_selected():
    participant_last_name_new = request.form['last_name_new']
    participant_first_name_new = request.form['first_name_new']
    participant_gender_new = request.form['gender_new']
    participant_year_new_str = request.form['year_new']

    # year must be covertable to int
    try:
        participant_year_new = int(participant_year_new_str)
    except:
        return render_template('participants/participants_edit_menu_fail.html',
                               data=ParticipantModel.get_participants_ordered())

    # end year must be lower the current year
    year_now = time_funcs.get_calendar_year()
    if participant_year_new > year_now:
        return render_template('participants/participants_edit_menu_fail.html',
                               data=ParticipantModel.get_participants_ordered())

    participant = ParticipantModel.get_by_id(session['participant_id_to_edit'])
    session['participant_id_to_edit'] = None

    try:
        participant.last_name = participant_last_name_new
        participant.first_name = participant_first_name_new
        participant.gender = participant_gender_new
        participant.year = participant_year_new
        participant.save_to_db()
        return render_template('participants/participants_edit_menu_success.html',
                               data=ParticipantModel.get_participants_ordered())
    except:
        return render_template('participants/participants_edit_menu_fail.html',
                               data=ParticipantModel.get_participants_ordered())


@participants_blueprint.route('/list', methods=['GET', 'POST'])
def list():
    # Not used at the moment
    if request.method == 'POST':
        year_filter = request.form['year'].strip()
        if year_filter != "":
            # found = RunnerModel.find_by_year(year_filter)
            filtered = [runner.json() for runner in ParticipantModel.find_by_year(year_filter)]
            return render_template('participants/registered.html', data=filtered)

    registered = [runner.json() for runner in ParticipantModel.list_all()]
    registered_count = len(registered)

    return render_template('participants/registered.html', data=registered, registered_count=registered_count)


@participants_blueprint.route('/import', methods=['GET', 'POST'])
def mass_import():
    """
    It is anticipated that the file format is OK.
    """
    # TODO implement file format check.

    if request.method == 'POST':

        # check if the post request has the file part
        if 'InputFile' not in request.files:
            return render_template('participants/mass_import.html')

        file = request.files['InputFile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return render_template('participants/mass_import_no_file_selected.html')

        if file and MassImport.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #filefolder = os.path.join(os.path.dirname(os.getcwd()), UPLOAD_FOLDER_NAME)
            filefolder = os.path.join(os.getcwd(), UPLOAD_FOLDER_NAME)
            abs_path = os.path.join(filefolder, filename)
            file.save(abs_path)

            if MassImport.insert_many(abs_path):
                # success import
                return render_template('participants/mass_import_success.html')
            else:
                # invalid file path
                return render_template('participants/mass_import_failed.html')

    return render_template('participants/mass_import.html')


@participants_blueprint.route('/delete', methods=['GET', 'POST'])
def delete_admin():
    """
    Page for deleting various parts of database
    - Delete participants - including all startlists and results
    - Delete categories
    """
    return render_template('participants/delete_admin.html')


@participants_blueprint.route('/_delete_participants')
def delete_participants():
    """
    Deletes all participants, startlists and results. Categories stay.
    Function is called by a javascript/jquery
    """
    ParticipantModel.delete_all_rows()
    StartlistModel.delete_all_rows()
    StartlistNameModel.delete_all_rows()

    message = "Deleted all participants, startlists and results"
    return jsonify(result=message)


@participants_blueprint.route('/_delete_all_data')
def delete_all():
    """
    Deletes all participants, startlists and results and categories
    Function is called by a javascript/jquery
    """
    ParticipantModel.delete_all_rows()
    StartlistModel.delete_all_rows()
    StartlistNameModel.delete_all_rows()
    CategoryModel.delete_all_rows()

    message = "Deleted all data from the Database"
    return jsonify(result=message)
