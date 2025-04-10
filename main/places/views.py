from django.http import JsonResponse
from django.views import View
from .models import DiningPlace


class PlaceListView(View):
    def get(self, request):
        places = list(DiningPlace.objects.all()[:10].values())
        return JsonResponse({"places": places}, json_dumps_params={"ensure_ascii": False},
                            content_type="application/json; charset=utf-8")


class PlaceFilterView(View):
    def get(self, request):
        # List of search terms
        search_terms = ['aaark', '6 a.m.', 'jinju', 'эроплан', 'kiosk', 'zoe',
                        'Lucky Izakaya Bar', 'Мaya', 'Моя рьяnaya babyшка летит v cingaпур',
                        'White Rabbit', 'Finch', 'Лицей', 'Кафе Кривоколенный 9с3', 'Jeffreys coffee',
                        'SurfCoffee', 'ABC Coffee Roasters', 'Surf Coffee x Solyanka',
                        'Skuratov coffee roasters', 'Resurant by Deep Fried Friends', 'Blanc',
                        'Saray', 'Sage', 'Mamie Bistro', 'Ресторан «800 Contemporary Steak»',
                        'Ресторан Big Wine Freaks', 'Riesling Boyz', 'КМ 20', 'Nothing Fancy',
                        'Saviv', 'Dizengof99', 'Ресторан «Shiba»', 'Sapiens', 'EVA',
                        'Mates', 'Кафе Nude', 'Салют', 'TEHNIKUM', 'Валенок', 'Пробка', 'Loona',
                        'Moments', 'BLOOM-N-BREW', 'Горыныч', 'Ikura', 'Skuratov', 'Jpan bistro',
                        'Linbistro', 'AVA bistro', 'Grace bistro', 'AVA', 'Avrora', 'From Berlin',
                        'KU Рамен Изакая Бар', 'Ikra', 'Bagebi', 'Страна которой нет', 'Ресторан IL Ristorante',
                        'Steak it easy', 'Вкусно - и точка', 'Tacobar', 'Sporco Pizza', 'kido', 'Subzero',
                        'Пицца 22 сантиметра', 'Zotman pizza', 'KFC', 'Rebellion Clubhouse Moscow',
                        'Ресторан «Ruski»', 'Self Edge Japanese', 'Hite Корейский ресторан']

        places = DiningPlace.objects.filter(
            name__icontains=search_terms[0]
        )

        for term in search_terms[1:]:
            places = places | DiningPlace.objects.filter(name__icontains=term)

        # Serialize the result to JSON and return as a response
        places_data = list(places.values('id', 'name', 'category', 'address', 'photo_link', 'description', 'rating'))

        return JsonResponse({"places": places_data}, json_dumps_params={"ensure_ascii": False},
                            content_type="application/json; charset=utf-8")
