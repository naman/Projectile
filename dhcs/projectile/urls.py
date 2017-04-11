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
                       # new pages
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
                       # modals
                       url(r'^filter/$', views.filter, name='filter'),
                       url(r'^apply/(?P<projectid>\d+)/$',
                           views.apply, name='apply'),
                       url(r'^withdraw/(?P<projectid>\d+)/$',
                           views.withdraw, name='withdraw'),
                       url(r'^profile/$', views.profile, name='profile'),

                       # old pages
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
                       url(r'^project/(?P<projectid>\d+)/apply/$',
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
                       url(r'^project/(?P<projectid>\d+)/selections/$',
                           views.adminprojectselected, name='adminprojectselected'),

                       url(r'files/resume/(.+)', views.fileview, name='fileview'),
                       url(r'files/projectfiles/(.+)',
                           views.docfileview, name='docfileview'),
                       url(r'search/results/$', views.search, name='search'),
                       url(r'^feedback/$', views.feedback, name='feedback'),
                       )
