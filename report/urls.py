from django.urls import path
from report import views

urlpatterns = [
    # report
    path("all", views.get_all_Report),
    path("report/<str:user_id>/user", views.get_report_by_user),
    path("report/<str:report_id>", views.ReportAPIView.as_view()),
    path("report", views.ReportAPIView.as_view()),
    # ReportComment
    path("report-comment/<str:report_id>/report", views.get_reportComment_by_report),
    path("report-comment/<str:comment_id>", views.ReportCommentAPIView.as_view()),
    path("report-comment", views.ReportCommentAPIView.as_view()),
    # ReportState
    path("report-state", views.ReportStateAPIView.as_view()),
    path("report-state/<str:state_id>", views.ReportStateAPIView.as_view()),
    path("report-state/<str:report_id>/report", views.get_ReportState_by_report),
]
