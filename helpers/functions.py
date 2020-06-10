from urllib.parse import urlencode
from django.urls import reverse
from django.shortcuts import redirect

def redirect_handler(request, url_name, options):
    base_url = reverse(url_name)
    # {next:"/"}
    query_string = urlencode(options) #?next=?
    url = "{}?{}".format(base_url, query_string)
    return redirect(url)

def get_numbers(string):
    stringArray = ''.join((ch if ch in '0123456789.-e' else ' ') for ch in string)
    return [int(i) for i in stringArray.split()]