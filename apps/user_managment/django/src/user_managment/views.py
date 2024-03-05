from django.http import JsonResponse

def test_endpoint(request):
    # Création d'un objet de données pour la démonstration
    data = {
        'message': 'Réponse du service user_managment',
        'info': 'Ceci est un test.'
    }
    
    # Retourner les données sous forme de JSON
    return JsonResponse(data)
