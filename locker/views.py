# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse

from django.utils import timezone
from locker.models import Lock
from locker.locking import *

# Create your views here.
def openLock(request):
  code = request.GET.get('code', '')
  computer = request.GET.get('computer', '')
  username = request.GET.get('username', '')
  thelock = Lock.objects.filter(code=code)

  if thelock.count() == 0:
    # invalid code
    return HttpResponse('Ta koda ne obstaja.')
  else:
    # valid code
    thelock = thelock[0]
    if checkIfExpired(thelock):
      # code expired
      return HttpResponse('Ta koda je potekla.')
    else:
      # code hasn't yet expired
      if not thelock.opened:
        # code was never opened
        thelock.opened = True
        thelock.activated_at = timezone.localtime()
        thelock.computer = computer
        thelock.username = username
        thelock.save()
      else:
        # code was already open, it has computer and user strings
        # check if computer strings match
        if thelock.computer != computer:
          return HttpResponse('Ta koda je že bila uporabljena na drugem računalniku. :/')
        # check if username strings match
        if thelock.username != username:
          return HttpResponse('To kodo je že uporabil drug uporabnik. :/')
  
  return HttpResponse(1)
