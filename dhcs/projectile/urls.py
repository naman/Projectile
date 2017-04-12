# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

from django.conf.urls import patterns, url
from projectile import views

handler404 = 'views.my_404_view'

urlpatterns = patterns('',
                       # modals
                       url(r'^filter/$', views.filter, name='filter'),
                       url(r'^apply_modal/(?P<projectid>\d+)/$',
                           views.apply_modal, name='apply_modal'),
                       url(r'^profile/$', views.profile, name='profile'),

                       url(r'^professor/(?P<profid>.*)/$',
                           views.student_professor, name='student_professor'),
                       url(r'^requests/$', views.admin_notifications,
                           name='admin_notifications'),
                       url(r'^professor/$', views.student_professors,
                           name='student_professors'),
                       url(r'^professor_profile/$', views.professor_profile,
                           name='professor_profile'),
                       url(r'^profile_modal/(?P<studid>\d+)/$', views.profile_modal,
                           name='profile_modal'),
                       url(r'^$', views.home, name='home'),
                       url(r'^logout/$', views.logout, name='logout'),
                       url(r'^needlogin/$', views.needlogin, name='needlogin'),
                       url(r'^newuser/$', views.newuser, name='newuser'),
                       url(r'^newadmin/$', views.newadmin, name='newadmin'),
                       url(r'^openproject/$', views.openproject,
                           name='openproject'),
                       url(r'^profile/$', views.profile, name='profile'),
                       url(r'^students/(?P<studentid>.*)/edit/$',
                           views.admineditstudent, name='admineditstudent'),
                       url(r'^project/(?P<projectid>\d+)/approve/(?P<applicantid>\d+)/$',
                           views.projectapprove, name='projectapprove'),
                       url(r'^project/(?P<projectid>\d+)/reject/(?P<applicantid>\d+)/$',
                           views.projectreject, name='projectreject'),
                       url(r'^project/(?P<projectid>\d+)/apply/(?P<appid>\d+)/$',
                           views.projectapply, name='projectapply'),
                       url(r'^project/(?P<projectid>\d+)/withdraw/$',
                           views.projectwithdraw, name='projectwithdraw'),
                       url(r'^project/(?P<projectid>\d+)/edit/$',
                           views.projectedit, name='projectedit'),
                       url(r'^project/(?P<projectid>\d+)/delete/$',
                           views.projectdelete, name='projectdelete'),
                       url(r'^project/(?P<projectid>\d+)/$',
                           views.projectpage, name='projectpage'),
                       url(r'^project/(?P<projectid>\d+)/getresume/$',
                           views.getresumes, name='projectgetresumes'),

                       url(r'files/resume/(.+)', views.fileview, name='fileview'),
                       url(r'files/projectfiles/(.+)',
                           views.docfileview, name='docfileview'),
                       url(r'search/results/$', views.search, name='search'),
                       url(r'^feedback/$', views.feedback, name='feedback'),
                       )
