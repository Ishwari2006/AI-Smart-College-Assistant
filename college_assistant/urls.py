from django.contrib import admin
from django.urls import path

from assistant.views import (
    # Public Home
    landing_page,

    # Student
    home,
    notices,
    assignments,
    timetable,
    faq,

    # AI Chatbot
    chatbot,
    chatbot_response,

    # Authentication
    user_logout,
    user_login,
    register,

    # Staff Dashboard
    staff_dashboard,

    # Staff - Notices
    staff_notices,
    staff_notice_add,
    staff_notice_edit,
    staff_notice_delete,

    # Staff - Assignments
    staff_assignments,
    staff_assignment_add,
    staff_assignment_edit,
    staff_assignment_delete,

    # Staff - Timetable
    staff_timetable,
    staff_timetable_add,
    staff_timetable_edit,
    staff_timetable_delete,

    # Staff - FAQ
    staff_faq,
    staff_faq_add,
    staff_faq_edit,
    staff_faq_delete,

    # Staff - Import College Data
    staff_import_data,
)


urlpatterns = [

    # =====================================================
    # ADMIN
    # =====================================================

    path(
        'admin/',
        admin.site.urls
    ),


    # =====================================================
    # PUBLIC HOME PAGE
    # =====================================================

    path(
        '',
        landing_page,
        name='home'
    ),


    # =====================================================
    # STUDENT DASHBOARD
    # =====================================================

    path(
        'dashboard/',
        home,
        name='dashboard'
    ),


    # =====================================================
    # STUDENT PAGES
    # =====================================================

    path(
        'notices/',
        notices,
        name='notices'
    ),

    path(
        'assignments/',
        assignments,
        name='assignments'
    ),

    path(
        'timetable/',
        timetable,
        name='timetable'
    ),

    path(
        'faq/',
        faq,
        name='faq'
    ),


    # =====================================================
    # AI CHATBOT
    # =====================================================

    path(
        'chatbot/',
        chatbot,
        name='chatbot'
    ),

    path(
        'chatbot-response/',
        chatbot_response,
        name='chatbot_response'
    ),


    # =====================================================
    # LOGIN / REGISTER / LOGOUT
    # =====================================================

    path(
        'login/',
        user_login,
        name='login'
    ),

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'logout/',
        user_logout,
        name='logout'
    ),


    # =====================================================
    # STAFF DASHBOARD
    # =====================================================

    path(
        'staff-dashboard/',
        staff_dashboard,
        name='staff_dashboard'
    ),


    # =====================================================
    # STAFF - NOTICES
    # =====================================================

    path(
        'staff/notices/',
        staff_notices,
        name='staff_notices'
    ),

    path(
        'staff/notices/add/',
        staff_notice_add,
        name='staff_notice_add'
    ),

    path(
        'staff/notices/edit/<int:id>/',
        staff_notice_edit,
        name='staff_notice_edit'
    ),

    path(
        'staff/notices/delete/<int:id>/',
        staff_notice_delete,
        name='staff_notice_delete'
    ),


    # =====================================================
    # STAFF - ASSIGNMENTS
    # =====================================================

    path(
        'staff/assignments/',
        staff_assignments,
        name='staff_assignments'
    ),

    path(
        'staff/assignments/add/',
        staff_assignment_add,
        name='staff_assignment_add'
    ),

    path(
        'staff/assignments/edit/<int:id>/',
        staff_assignment_edit,
        name='staff_assignment_edit'
    ),

    path(
        'staff/assignments/delete/<int:id>/',
        staff_assignment_delete,
        name='staff_assignment_delete'
    ),


    # =====================================================
    # STAFF - TIMETABLE
    # =====================================================

    path(
        'staff/timetable/',
        staff_timetable,
        name='staff_timetable'
    ),

    path(
        'staff/timetable/add/',
        staff_timetable_add,
        name='staff_timetable_add'
    ),

    path(
        'staff/timetable/edit/<int:id>/',
        staff_timetable_edit,
        name='staff_timetable_edit'
    ),

    path(
        'staff/timetable/delete/<int:id>/',
        staff_timetable_delete,
        name='staff_timetable_delete'
    ),


    # =====================================================
    # STAFF - FAQ
    # =====================================================

    path(
        'staff/faq/',
        staff_faq,
        name='staff_faq'
    ),

    path(
        'staff/faq/add/',
        staff_faq_add,
        name='staff_faq_add'
    ),

    path(
        'staff/faq/edit/<int:id>/',
        staff_faq_edit,
        name='staff_faq_edit'
    ),

    path(
        'staff/faq/delete/<int:id>/',
        staff_faq_delete,
        name='staff_faq_delete'
    ),


    # =====================================================
    # STAFF - IMPORT COLLEGE DATA
    # =====================================================

    path(
        'staff/import-data/',
        staff_import_data,
        name='staff_import_data'
    ),

]