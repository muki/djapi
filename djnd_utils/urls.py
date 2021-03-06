"""djnd_utils URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from counter.views import *
from djnd_landing.views import *

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add/(?P<type_>[\w].+)', plusOne),
    url(r'^counter/(?P<type_>[\w].+)', getCoutner),
    url(r'^sign/', addSignature),
    url(r'^sign-no-mail/', addSignatureNoMail),
    url(r'^sign-mail/', addSignatureMail),
    url(r'^getNumberOfSignatures/', getNumberOfSignatures),
    url(r'^getAllSignatures/', getAllSignatures),
    url(r'^postman/', sender),
    url(r'^djndLanding/(?P<category>\w+)/$', getExposed),
    url(r'^djndLanding/(?P<category>\w+)/(?P<num_of_news>\d+)/$', getExposed),
    url(r'^getExposed/(?P<category>\w+)/$', getExposed),
    url(r'^getExposed/(?P<category>\w+)/(?P<num_of_news>\d+)/$', getExposed),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^getKuraSignatures/', getFasterKura),
    url(r'^getAllSignaturesAndCountForMultiple/', getAllSignaturesAndCountForMultiple),
    url(r'^getPublicSignaturesAndFullCountForMultiple/', getPublicSignaturesAndFullCountForMultiple),
    url(r'^sendTweet/', sendTweet),
    url(r'^sendMailParlameterOrg', sendMailParlameterOrg),

    url(r'^locker/', include('locker.urls')),
]
