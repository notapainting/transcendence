# blockchain/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import asyncio
from .blockchain import record_match_on_blockchain

@csrf_exempt
async def register_match(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            tournament_id = data['tournament_id']
            winner = data['winner']
            loser = data['loser']
            winner_score = data['winner_score']
            loser_score = data['loser_score']


            await record_match_on_blockchain(tournament_id, winner, loser, winner_score, loser_score)


            return JsonResponse({'status': 'success', 'message': 'Match enregistré sur la blockchain.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
