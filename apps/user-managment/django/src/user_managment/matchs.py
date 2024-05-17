from django.db import models
# import user_managment.models as mod


class MatchResults(models.Model):
    # user1 = models.ForeignKey(mod.CustomUser, related_name='matchs')
    # user2 = models.ForeignKey(mod.CustomUser, related_name='opponents')
    user_one = models.CharField(max_length=50)
    user_one_score = models.IntegerField()
    user_one_powerups = models.IntegerField()
    user_two = models.CharField(max_length=50)
    user_two_score = models.IntegerField()
    user_two_powerups = models.IntegerField()
    # match_start = models.DateTimeField()
    # match_end = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user_one} {self.user_one_score} - {self.user_two_score} {self.user_two}"

# Json test:
# curl -k -X POST -H "Content-Type: application/json" -d @match1.json https://localhost:8443/matchsinfos/
# curl -k -X GET  https://localhost:8443/matchsinfos/
