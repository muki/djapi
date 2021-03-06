# -*- coding: utf-8 -*-

from django.shortcuts import render
from .models import Vote, MailAddress
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from HTMLParser import HTMLParser

import os
import tweepy
import requests

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# Create your views here.

def index(request):
    return HttpResponse("")

def plusOne(request, type_):
	Vote(type_of=type_).save()
	return HttpResponse("Added")


def getCoutner(request, type_):
	count = Vote.objects.filter(type_of=type_).count()
	return HttpResponse(count)


@csrf_exempt
def sender(request):
	if request.method == 'POST':
		content = request.POST["content"]
		send_mail(
			'Sprejemanje študentske zakonodaje',
			content,
			settings.DEFAULT_FROM_EMAIL,
			['cofek0@gmail.com'],
			fail_silently=False,
		)
	else:
		return HttpResponse("Neki ni ql")
	return HttpResponse("Sent")


def addSignature(request):
	name = strip_tags(request.GET.get('name', ''))
	email = strip_tags(request.GET.get('email', ''))
	peticija = request.GET.get('peticija', '')
	if peticija and name and email:
		MailAddress(e_mail=email, type_of=peticija, name=name).save()
		return HttpResponse("Saved")
	return HttpResponse('Napaka, manjkajo parametri!')


@csrf_exempt
def addSignatureMail(request):
    if request.method == 'POST':
        peticija = request.POST.get('peticija', '')
        name = strip_tags(request.POST.get('name', ''))
        email = strip_tags(request.POST.get('email', ''))
        subject = strip_tags(request.POST.get('subject', ''))
        content = request.POST.get('content', '')
        if peticija and name and email and subject and content:
            MailAddress(e_mail=email, type_of=peticija, name=name).save()

            referer = request.META.get('HTTP_REFERER', '')
            if '//danesjenovdan.si/' in referer:
                requests.post(
                    settings.MAILGUN_API,
                    auth=('api', settings.MAILGUN_ACCESS_KEY),
                    data={
                        'from': settings.FROM_MAIL,
                        'to': email,
                        'subject': subject,
                        'text': strip_tags(content),
                        'html': content,
                    }
                )

            return HttpResponse('Saved')
        return HttpResponse('Napaka, manjkajo parametri!')
    return HttpResponse('Napaka!')

@csrf_exempt
def addSignatureNoMail(request):
    name = strip_tags(request.GET.get('name', ''))
    email = strip_tags(request.GET.get('email', ''))
    peticija = request.GET.get('peticija', '')
    if peticija and name:
        MailAddress(e_mail=email, type_of=peticija, name=name).save()
        response = HttpResponse("Saved")
    else:
	response = HttpResponse('Napaka, manjkajo parametri!')

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

    return response


@csrf_exempt
def sendMailParlameterOrg(request):
    if request.method == 'POST':
        name = strip_tags(request.POST.get('name', ''))
        organization = strip_tags(request.POST.get('organization', ''))
        email = strip_tags(request.POST.get('email', ''))
        message = strip_tags(request.POST.get('message', ''))
        if name and organization and email and message:
            # referer = request.META.get('HTTP_REFERER', '')
            # if '//parlameter.org/' in referer:
            requests.post(
                settings.MAILGUN_API,
                auth=('api', settings.MAILGUN_ACCESS_KEY),
                data={
                    'from': settings.FROM_MAIL,
                    'to': 'vsi@danesjenovdan.si',
                    'subject': 'Parlameter.org - contact from: ' + name,
                    'text': 'Name: ' + name + '\n' +
                            'Organization: ' + organization + '\n' +
                            'Email: ' + email + '\n' +
                            'Message: \n\n' + message,
                    'h:Reply-To': email,
                }
            )

            return HttpResponse('Sent')
        return HttpResponse('Error: Missing parameters')
    return HttpResponse('Error')


def getAllSignatures(request):
	peticija = request.GET.get('peticija', '')
	names = MailAddress.objects.filter(type_of=peticija).values_list('name', flat=True)
	out = ', '.join(list(names))
	return HttpResponse(out)

def getNumberOfSignatures(request):
	peticija = request.GET.get('peticija', '')
	mail_count = MailAddress.objects.filter(type_of=peticija).count()
	return HttpResponse(str(mail_count))


def getAllSignaturesAndCountForMultiple(request):
    peticije = request.GET.get('peticije', '')

    out = ''
    counter = 0

    if peticije:
        peticije = peticije + '.'
        all_emails = MailAddress.objects.filter(type_of__startswith=peticije).values_list('name', 'e_mail')

        email_set = set()
        all_emails = [email_set.add(e[1]) or e[0] for e in all_emails if e[1] not in email_set]

        out = ', '.join(all_emails)
        counter = len(all_emails)

    return JsonResponse({'names': out, 'counter': counter})


def getPublicSignaturesAndFullCountForMultiple(request):
    peticije = request.GET.get('peticije', '')

    out = ''
    counter = 0

    if peticije:
        # get all names and emails for signatures that start with "name."
        peticije = peticije + '.'
        all_signatures_qs = MailAddress.objects.filter(type_of__startswith=peticije)
        all_signatures = all_signatures_qs.values_list('name', 'e_mail')
        # only take one signature per email
        email_set = set()
        all_names_for_unique_emails = [email_set.add(e[1]) or e[0] for e in all_signatures if e[1] not in email_set]
        # count number of signatures
        counter = len(all_names_for_unique_emails)
        # exclude private names
        peticije_private = peticije + 'private.'
        exclude_emails = MailAddress.objects.filter(type_of__startswith=peticije_private).values_list('e_mail', flat=True)
        all_public_signatures = all_signatures_qs.exclude(e_mail__in=exclude_emails).values_list('name', 'e_mail')
        # only take one signature per email
        email_set = set()
        all_public_names_for_unique_emails = [email_set.add(e[1]) or e[0] for e in all_public_signatures if e[1] not in email_set]
        # join all names
        out = ', '.join(all_public_names_for_unique_emails)

    return JsonResponse({'names': out, 'counter': counter})


def getKura(request):
	peticije = ['imasjajca.djndtrue.dzzztrue', 'imasjajca.djndtrue.dzzzfalse', 'imasjajca.djndfalse.dzzzfalse', 'imasjajca.djndfalse.dzzztrue']
	hide = 'imasjajcaHIDE'
	all_mails = MailAddress.objects.filter(type_of__in=peticije)

	visited = []
	duplicated = []
	mejlz = []
	for mail in all_mails:
		if mail.e_mail in visited:
			duplicated.append(mail.id)
			mejlz.append(mail.e_mail)
		else:
			visited.append(mail.e_mail)

	counter = all_mails.count()
	all_mails = all_mails.exclude(id__in=duplicated)

	exclude = MailAddress.objects.filter(type_of=hide)
	all_mails=all_mails.exclude(e_mail__in=exclude.values_list("e_mail", flat=True))
	names = all_mails.values_list('name', flat=True)
	out = ', '.join(list(names))
	return JsonResponse({'names': out, 'counter': counter})


def getFasterKura(request):
    peticije = ['imasjajca.djndtrue.dzzztrue', 'imasjajca.djndtrue.dzzzfalse', 'imasjajca.djndfalse.dzzzfalse', 'imasjajca.djndfalse.dzzztrue']
    hide = 'imasjajcaHIDE'

    exclude_emails = MailAddress.objects.filter(type_of=hide).values_list('e_mail', flat=True)
    all_emails = MailAddress.objects.filter(type_of__in=peticije).exclude(e_mail__in=exclude_emails).values_list('name', 'e_mail')

    email_set = set()
    all_emails = [email_set.add(e[1]) or e[0] for e in all_emails if e[1] not in email_set]

    out = ', '.join(all_emails)
    return JsonResponse({'names': out, 'counter': len(all_emails)})


def exportKura():
    peticije = ['imasjajca.djndtrue.dzzztrue', 'imasjajca.djndtrue.dzzzfalse', 'imasjajca.djndfalse.dzzzfalse', 'imasjajca.djndfalse.dzzztrue']

    all_emails = MailAddress.objects.filter(type_of__in=peticije).values_list('name', 'e_mail')

    email_set = set()
    all_emails = [email_set.add(e[1]) or e[0] for e in all_emails if e[1] not in email_set]
    print([name for name in all_emails])
    with open('all.txt','w') as out:
        out.writelines([str(name.encode('utf-8').strip() + "\n") for name in all_emails])

 
def exportKuraDJND():
    peticije = ['imasjajca.djndtrue.dzzztrue', 'imasjajca.djndtrue.dzzzfalse']

    all_emails = MailAddress.objects.filter(type_of__in=peticije).values_list('name', 'e_mail')

    email_set = set()
    all_emails = [email_set.add(e[1]) or e[0] for e in all_emails if e[1] not in email_set]
    print([name for name in all_emails])
    with open('all.txt','w') as out:
        out.writelines([str(name.encode('utf-8').strip() + "\n") for name in all_emails])


@csrf_exempt
def sendTweet(request):
    if request.method == 'POST':
        secret = request.POST.get('secret', '')
        image_url = request.POST.get('image_url', '')
        tweet_text = strip_tags(request.POST.get('tweet_text', ''))
        if secret and tweet_text:
            if secret == settings.TWITTER_SEND_TWEET_SECRET:
                auth = tweepy.OAuthHandler(settings.TWITTER_API['consumer_key'], settings.TWITTER_API['consumer_secret'])
                auth.set_access_token(settings.TWITTER_API['access_token'], settings.TWITTER_API['access_token_secret'])
                api = tweepy.API(auth)

                if image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
                    filename = 'tweet_temp.jpg'
                    request = requests.get(image_url, stream=True)
                    if request.status_code == 200:
                        with open(filename, 'wb') as image:
                            for chunk in request:
                                image.write(chunk)

                        status = api.update_with_media(filename, status=tweet_text)
                        os.remove(filename)
                    else:
                        return HttpResponse('Napaka! (image_url)', status=400)
                else:
                    status = api.update_status(status=tweet_text)  # status = tweet 

                return HttpResponse('Poslano!')
            return HttpResponse('Napaka! (secret)', status=400)
        return HttpResponse('Napaka! (params)', status=400)
    return HttpResponse('Napaka!', status=400)
