from django.db import models
from user_managment.models import CustomUser


class MatchResults(models.Model):
    host = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True, related_name="user_1")
    host_name = models.CharField(max_length=100, blank=True, null=True)
    host_score = models.IntegerField()
    host_powerups = models.IntegerField()
    client = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True, related_name="user_2")
    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_score = models.IntegerField()
    client_powerups = models.IntegerField()
    match_start = models.DateTimeField(blank=True, null=True)
    match_end = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    def __str__(self):
        return f"{self.match_end}: {self.host_name} {self.host_score} - {self.client_score} {self.client_name}"

# Json test:
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:8443/matchsinfos/
# curl -k -X GET  https://localhost:8443/matchsinfos/
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:443/matchsinfos/
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match2.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match3.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match4.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match5.json https://localhost:443/matchsinfos/
# curl -k -X GET  https://localhost:443/matchsinfos/
