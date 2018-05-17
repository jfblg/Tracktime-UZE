from flask import Blueprint, request, render_template, session, redirect, url_for

from src.models.categories.categories import CategoryModel, CategoryAddForm
from src.common.utils import time_funcs

categories_blueprint = Blueprint('categories', __name__)


@categories_blueprint.route('/list', methods=['GET'])
def list():
    loaded_data = [category.json() for category in CategoryModel.list_all()]
    category_count = len(loaded_data)
    return render_template('categories/categories_list.html', data=loaded_data, category_count=category_count)


@categories_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    form = CategoryAddForm(request.form)
    if request.method == 'POST' and form.validate():
        input_data = dict()
        input_data['category_name'] = request.form['category_name'].strip()
        input_data['gender'] = request.form['gender']
        input_data['year_start'] = request.form['year_start'].strip()
        input_data['year_end'] = request.form['year_end'].strip()

        new_category = CategoryModel(**input_data)
        new_category.save_to_db()
        return render_template('categories/categories_add_success.html', form=form, data=input_data)

    return render_template('categories/categories_add.html', form=form)


@categories_blueprint.route('/show_categories_to_delete', methods=['GET', 'POST'])
def show_categories_to_delete():
    return render_template('categories/categories_delete_menu.html',
                           data=CategoryModel.list_categories_ordered())


@categories_blueprint.route('/delete_selected_category', methods=['POST'])
def delete_selected_category():
    category_id = request.form['category_select']
    category = CategoryModel.find_by_id(category_id)
    try:
        category.delete_from_db()
        return render_template('categories/categories_delete_menu_success.html',
                           data=CategoryModel.list_categories_ordered())
    except:
        return render_template('categories/categories_delete_menu_fail.html',
                               data=CategoryModel.list_categories_ordered())


@categories_blueprint.route('/show_categories_to_edit', methods=['GET', 'POST'])
def show_categories_to_edit():
    return render_template('categories/categories_edit_menu.html',
                           data=CategoryModel.list_categories_ordered())


@categories_blueprint.route('/show_category_to_edit', methods=['POST'])
def show_category_to_edit():
    category_id = request.form['category_select']
    category = CategoryModel.find_by_id(category_id)

    # save category_id to session for the function edit_selected_category
    session['category_id_to_edit'] = category_id

    return render_template('categories/categories_edit_selected.html',
                           category_name=category.category_name,
                           gender=category.gender,
                           year_start=category.year_start,
                           year_end=category.year_end)


@categories_blueprint.route('/edit_selected_category', methods=['POST'])
def edit_selected_category():
    category_name_new = request.form['category_name_new']
    gender_new = request.form['gender_new']
    year_start_new_str = request.form['year_start_new']
    year_end_new_str = request.form['year_end_new']

    # year must be covertable to int
    try:
        year_start_new = int(year_start_new_str)
        year_end_new = int(year_end_new_str)
    except:
        return render_template('categories/categories_edit_menu_fail.html',
                               data=CategoryModel.list_categories_ordered())

    # end year must be lower the current year
    year_now = time_funcs.get_calendar_year()
    if year_end_new > year_now:
        return render_template('categories/categories_edit_menu_fail.html',
                               data=CategoryModel.list_categories_ordered())

    # year_start must be lower or equal to end yeaer
    if year_start_new > year_end_new:
        return render_template('categories/categories_edit_menu_fail.html',
                               data=CategoryModel.list_categories_ordered())

    category = CategoryModel.find_by_id(session['category_id_to_edit'])
    session['category_id_to_edit'] = None

    try:
        category.category_name = category_name_new
        category.gender = gender_new
        category.year_start = year_start_new
        category.year_end = year_end_new
        category.save_to_db()
        return render_template('categories/categories_edit_menu_success.html',
                               data=CategoryModel.list_categories_ordered())
    except:
        return render_template('categories/categories_edit_menu_fail.html',
                               data=CategoryModel.list_categories_ordered())
