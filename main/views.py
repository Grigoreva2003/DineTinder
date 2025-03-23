from django.shortcuts import render
from .utils import load_json_data

def landing_page(request):
    header_data = load_json_data('header.json')
    footer_data = load_json_data('footer.json')
    landing_data = load_json_data('landing.json')

    context = {
        'header_data': header_data,
        'footer_data': footer_data,
        'landing_data': landing_data
    }
    return render(request, 'landing.html', context)