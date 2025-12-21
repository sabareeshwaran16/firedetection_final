from django.db import models
from django.utils import timezone

class DetectionLog(models.Model):
    DETECTION_TYPES = [
        ('fire', 'Fire'),
        ('smoke', 'Smoke'),
        ('both', 'Fire & Smoke'),
    ]
    
    detection_type = models.CharField(max_length=10, choices=DETECTION_TYPES)
    confidence = models.FloatField()
    image_path = models.CharField(max_length=255, blank=True)
    detected_at = models.DateTimeField(default=timezone.now)
    alert_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.detection_type} - {self.confidence:.2f} - {self.detected_at}"