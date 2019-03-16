from django.http import HttpResponseForbidden

class FilterHostMiddleware(object):
    def __init__(self, process_request):
        self.process_request = process_request

    def __call__(self, request):
        response = self.process_request(request)

        allowed_hosts = ['127.0.0.1', 'localhost']  # specify complete host names here
        host = request.META.get('HTTP_HOST')

        if host[len(host)-10:] == 'dyndns.org':  # if the host ends with dyndns.org then add to the allowed hosts
            allowed_hosts.append(host)
        elif host[:7] == '192.168':  # if the host starts with 192.168 then add to the allowed hosts
            allowed_hosts.append(host)

        if host not in allowed_hosts:
            return HttpResponseForbidden()

        return response


        
