from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.form_signin, name='signin'),
    path('feature/', views.feature, name='feature'),
    path('faq/', views.faq, name='faq'),
    path('pricing/', views.pricing, name='pricing'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('signup/', views.form_signup, name='signup'),
    path("successful_login/", views.successful_login, name="successful_login"),
    path('customer_discovery/', views.customer_discovery, name='customer_discovery'),
    path('outbound_calls/', views.outbound_calls, name='outbound_calls'),
    path('inbound_calls/', views.inbound_calls, name='inbound_calls'),

    # ✅ Each personality now calls the DRY handler internally
    path('outbound_call_1/', views.fred_davis, name='fred_davis'),
    path('outbound_call_2/', views.jordan_reyes, name='jordan_reyes'),
    path('outbound_call_3/', views.alex_martinez, name='alex_martinez'),
    path('outbound_call_4/', views.priya_shah, name='priya_shah'),
    path('outbound_call_5/', views.chase_montgomery_III, name='chase_montgomery_III'),
    path('outbound_call_6/', views.sofia_delgado, name='sofia_delgado'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('leaderboard/', views.dealership_leaderboard, name='dealership_leaderboard'),
    path('call-history/<str:assistant_name>/', views.call_history_fred_davis, name='call_history_fred_davis'),
    path("api/call-record/<str:call_id>/", views.call_record_api, name="call_record_api"),
]
