'''
from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
import os
from django.template.loader import get_template
from django.conf import settings

# Create your views here.
def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

def render_pdf_view(request):
    template_path = 'Borang mohon kenderaan.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display:
    response['Content-Disposition'] = 'filename="report2.pdf"'
    # # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
'''
from django.shortcuts import render,redirect
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def render_pdf_view(request, Name, Start, End, participant, destination, reason):
    
    request.session['reason'] = reason
    request.session['participant'] = participant
    request.session['destination'] = destination
    request.session['Name'] = Name
    request.session['Start'] = Start
    request.session['End'] = End
    template_path = 'Borang mohon kenderaan.html'
    context = {'myvar': 'this is your template context'}
    template = get_template(template_path)
    html = template.render(context)
    
    # Generate a unique file name for the PDF file
    filename = 'report.pdf'
    while os.path.exists(os.path.join(settings.BASE_DIR, 'pdf', 'pdf_save', filename)):
        filename = '_' + filename

    # Set the file path for the PDF file
    file_path = os.path.join(settings.BASE_DIR, 'pdf', 'pdf_save', filename)

    # Generate the PDF and write it to the file
    with open(file_path, 'wb') as file:
        pisa_status = pisa.CreatePDF(html, dest=file, link_callback=link_callback)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

    # Send a response to the client to confirm that the PDF has been saved
    response = HttpResponse('PDF file saved to ' + file_path)
    return redirect('/')
