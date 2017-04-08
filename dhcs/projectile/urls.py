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
                       url(r'^student_professor/$',
                           views.student_professor, name='student_professor'),
                       url(r'^add_project/$', views.professor_addproject,
                           name='professor_addproject'),
                       url(r'^requests/$', views.admin_notifications,
                           name='admin_notifications'),
                       url(r'professors/$', views.student_professors,
                           name='student_professors'),

                       # modals
                       url(r'^filter/$', views.filter, name='filter'),
                       url(r'^apply/$', views.apply, name='apply'),
                       url(r'^profile/$', views.profile, name='profile'),

                       # old pages
                       url(r'^$', views.home, name='home'),
                       url(r'^logout/$', views.logout, name='logout'),
                       url(r'^needlogin/$', views.needlogin, name='needlogin'),
                       url(r'^newuser/$', views.newuser, name='newuser'),
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
                       url(r'^project/(?P<projectid>\d+)/applicants/$',
                           views.projectapplicants, name='projectapplicants'),
                       url(r'^project/(?P<projectid>\d+)/$',
                           views.projectpage, name='projectpage'),

                       url(r'^project/(?P<projectid>\d+)/getresume/$',
                           views.getresumes, name='projectgetresumes'),
                       # url(r'^project/(?P<projectid>\d+)/getcsv/$',
                       # views.getprojectcsv, name='projectgetcsvs'),
                       url(r'^project/(?P<projectid>\d+)/selections/$',
                           views.adminprojectselected, name='adminprojectselected'),
                       url(r'^myapplications/$', views.myapplications,
                           name='myapplications'),
                       url(r'files/resume/(.+)', views.fileview, name='fileview'),
                       url(r'files/projectfiles/(.+)',
                           views.docfileview, name='docfileview'),

                       url(r'search/results/$', views.search, name='search'),
                       url(r'^feedback/$', views.feedback, name='feedback'),
                       )
