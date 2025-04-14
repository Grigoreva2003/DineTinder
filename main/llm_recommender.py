import google.generativeai as genai
from main.defs import GEMINI_API_KEY


class GeminiRecommender:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def get_recommendation(self, favorite_places, candidate_places):
        """Generate a personalized recommendation using Gemini"""
        prompt = "На основе списка избранных заведений:\n\n"

        # Add favorite places
        for place in favorite_places:
            prompt += f"Название: {place.name}\n" \
                      f"Рейтинг: {place.rating}\n" \
                      f"Описание: {place.description[:300]}\n\n"

        prompt += "\nПорекомендуй для пользователя одно место из списка кандидатов:\n\n"

        # Add candidate places with IDs
        for place in candidate_places:
            prompt += f"place_id {place.id}\n" \
                      f"Название: {place.name}\n" \
                      f"Рейтинг: {place.rating}\n" \
                      f"Описание: {place.description[:300]}\n\n"

        prompt += "\nВ ответе рекомендации напиши только place_id и небольшое персонализированное описание места" \
                  " для пользователя (не более 150 символов). " \
                  "В ответе не должно присутствовать вопросов к пользователю. " \
                  "В персонализированном описании можешь использовать информацию о предпочтениях пользователя, " \
                  "описании заведения. Информацию о рейтинге заведения использую обощенно." \
                  "Название заведения и place_id использовать не надо." \
                  "Посоветуй одно место из списка кандидатов." \
                  "Ответ должен быть в формате:\n" \
                  "place_id: <place_id>\ndescription: <персонализированное описание>\n"

        response = self.model.generate_content(prompt)
        recommendation_text = response.text

        try:
            if "place_id" in recommendation_text:
                place_id_text = recommendation_text.split("place_id: ")[1].split("\n")[0]
                if place_id_text.isdigit():
                    place_id = int(place_id_text)
                    personalized_text = recommendation_text.split("description: ")[1].split("\n")[0].strip()
                    return place_id, personalized_text
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")

        return (candidate_places[0].id,
                "Это заведение похоже на твои избранные места. Оно может попасть в их список! Попробуй")
