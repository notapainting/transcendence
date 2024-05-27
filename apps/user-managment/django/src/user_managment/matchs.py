from django.db import models
from user_managment.models import CustomUser


class MatchResults(models.Model):
    user_one = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True)
    user_one_name = models.CharField(max_length=100, blank=True, null=True)
    user_one_score = models.IntegerField()
    user_one_powerups = models.IntegerField()
    # user_two = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True)
    user_two = models.CharField(max_length=100, blank=True, null=True)
    user_two_name = models.CharField(max_length=100, blank=True, null=True)
    user_two_score = models.IntegerField()
    user_two_powerups = models.IntegerField()
    match_start = models.DateTimeField(blank=True, null=True)
    match_end = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    def __str__(self):
        return f"{self.match_end}: {self.user_one_name} {self.user_one_score} - {self.user_two_score} {self.user_two_name}"

# Json test:
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:8443/matchsinfos/
# curl -k -X GET  https://localhost:8443/matchsinfos/
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:443/matchsinfos/
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match2.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match3.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match4.json https://localhost:443/matchsinfos/ && curl -k -X POST -H "Content-Type: application/json" -d @match5.json https://localhost:443/matchsinfos/
# curl -k -X GET  https://localhost:443/matchsinfos/
