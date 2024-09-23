# blockchain/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import asyncio
import logging
from .blockchain import get_last_tournament_id, record_match_on_blockchain

from logging import getLogger
logger = getLogger('base')

@csrf_exempt
async def register_match(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tournament_id = data['tournament_id']
            winner = data['winner']
            loser = data['loser']
            winner_score = data['score_w']
            loser_score = data['score_l']

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, record_match_on_blockchain, tournament_id, winner, loser, winner_score, loser_score)

            return JsonResponse({'status': 'success', 'message': 'Match enregistré sur la blockchain.'})

        except KeyError as e:
            logger.error(f"Clé manquante dans la requête : {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'Clé manquante : {str(e)}'}, status=400)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur dans le parsing du JSON : {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': f'Erreur dans le format JSON : {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du match : {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Une erreur interne est survenue.'}, status=500)

    elif request.method == 'GET':
        try:
            loop = asyncio.get_running_loop()
            last_tournament_id = await loop.run_in_executor(None, get_last_tournament_id)

            return JsonResponse({'status': 'success', 'last_tournament_id': last_tournament_id})

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du dernier ID de tournoi : {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Une erreur interne est survenue.'}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)