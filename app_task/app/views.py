import calendar
from .models import Person, PersonGroup
from flask_appbuilder.views import ModelView, BaseView
from flask_appbuilder import ModelView, SimpleFormView, BaseView, expose, has_access
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.widgets import ListThumbnail
from app import app, db, appbuilder

import json
import logging
import requests
import tabulate
import ast


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import (Blueprint, request, make_response, jsonify)


engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()


class PersonModelView(ModelView):
    datamodel = SQLAInterface(Person, db.session)

    list_title = 'List Contacts'
    show_title = 'Show Contact'
    add_title = 'Add Contact'
    edit_title = 'Edit Contact'

    list_widget = ListThumbnail

    label_columns = {'person_group_id': 'Group', 'photo_img': 'Photo', 'photo_img_thumbnail': 'Photo'}
    list_columns = ['photo_img_thumbnail', 'name', 'birthday', 'person_group']

    show_fieldsets = [
        ('Summary', {'fields': ['photo_img', 'name', 'address', 'person_group']}),
        ('Personal Info',
         {'fields': ['birthday', 'personal_phone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['name', 'photo', 'address', 'person_group']}),
        ('Personal Info',
         {'fields': ['birthday', 'personal_phone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'photo', 'address', 'person_group']}),
        ('Personal Info',
        {'fields': ['birthday', 'personal_phone', 'personal_email'], 'expanded': False}),
        ('Professional Info',
         {'fields': ['business_function', 'business_email'], 'expanded': False}),
        ('Extra', {'fields': ['notes'], 'expanded': False}),
    ]


class GroupModelView(ModelView):
    datamodel = SQLAInterface(PersonGroup, db.session)
    related_views = [PersonModelView]

    label_columns = {'phone1': 'Phone (1)', 'phone2': 'Phone (2)', 'taxid': 'Tax ID'}
    list_columns = ['name', 'notes']

'''
class PersonChartView(GroupByChartView):
    datamodel = SQLAInterface(Person)
    chart_title = 'Grouped Persons'
    label_columns = PersonModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group': 'person_group',
            'series': [(aggregate_count,'person_group')]
        }
    ]
'''


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)

def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Person)

    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = PersonModelView.label_columns
    definitions = [
        {
            'group' : 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'group')]
        }
    ]




class MyView(BaseView):
    
    route_base = "/api/v1"

    @expose('/empdata', methods=['GET','POST'])
    def employee_data(self):
        emp_data = session.query(Person).filter().all()
        surveylist = []
        for i in emp_data:   
           surveylist.append({'name' : i.name, 'address' : i.address})
        return json.dumps(surveylist)


class GetView(BaseView):
    
    route_base = "/api/v1"


    @expose('/getdata', methods=['GET','POST'])
    def get_data(self):
        url = "http://localhost:8080/api/v1/empdata"
        response = requests.request("GET", url)
        data=json.loads(response.text)
        ult_list = ast.literal_eval(json.dumps(data))
        header = ult_list[0].keys()
        rows =  [x.values() for x in ult_list]
        return tabulate.tabulate(rows, header, tablefmt='rst')



class DataView(BaseView):
    
    route_base = "/api/v1"


    @expose('/systemdata', methods=['GET','POST'])
    def get_data(self):
        url = "http://10.60.37.41:8080/api/vi/empdataa"
        response = requests.request("GET", url)
        data=json.loads(response.text)
        ult_list = ast.literal_eval(json.dumps(data))
        header = ult_list[0].keys()
        rows =  [x.values() for x in ult_list]
        return tabulate.tabulate(rows, header, tablefmt='rst')




db.create_all()
appbuilder.add_view_no_menu(MyView())
appbuilder.add_view(MyView, "Expose", href="/api/v1/empdata", category='Task')
appbuilder.add_view(GetView, "Get Data", href="/api/v1/getdata", category='Task')
appbuilder.add_view(DataView, "Data", href="/api/v1/ipdata", category='Task')
appbuilder.add_link("Google", href="https://www.google.com/", icon = "fa-google-plus")
appbuilder.add_view(GroupModelView(), "List Groups", icon="fa-folder-open-o", category="Contacts")
appbuilder.add_view(PersonModelView(), "List Contacts", icon="fa-envelope", category="Contacts")
#appbuilder.add_view(PersonChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

