from main.utils.utils import load_json_data
from main.defs import VK_APP_ID, VK_REDIRECT_URI

def global_context(request):
    return {
        'header_data': load_json_data('header.json'),
        'footer_data': load_json_data('footer.json'),
        'VK_APP_ID': VK_APP_ID,
        'VK_REDIRECT_URI': VK_REDIRECT_URI,
    }
