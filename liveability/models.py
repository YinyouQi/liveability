from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class City(models.Model):
    """城市基础信息"""
    name = models.CharField(max_length=100)  #CharFiled文本字段用于国家名城市名
    country = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.name}, {self.country}"


class CityData(models.Model):
    """城市实时数据（来自 API，做缓存用）"""
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    aqi = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city.name} data @ {self.updated_at}"


class Preference(models.Model):
    """用户偏好"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    temp_min = models.FloatField()
    temp_max = models.FloatField()
    max_aqi = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}'s preference"


class FavoriteCity(models.Model):
    """用户收藏城市"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.city.name}"
    
    class Meta:
        unique_together = ('user', 'city')