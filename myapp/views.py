import cv2
import os
import json
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from ultralytics import YOLO
from .models import DetectionLog
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

# Load YOLO model
model_path = os.path.join(settings.BASE_DIR.parent, "best.pt")
model = YOLO(model_path)

@login_required(login_url='login')
def index(request):
    """Dashboard home page"""
    recent_logs = DetectionLog.objects.all()[:5]
    total_detections = DetectionLog.objects.count()
    fire_count = DetectionLog.objects.filter(detection_type='fire').count()
    smoke_count = DetectionLog.objects.filter(detection_type='smoke').count()
    
    context = {
        'recent_logs': recent_logs,
        'total_detections': total_detections,
        'fire_count': fire_count,
        'smoke_count': smoke_count,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def image_detect(request):
    """Image upload detection"""
    if request.method == "POST" and request.FILES.get("image"):
        try:
            uploaded = request.FILES["image"]
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            input_path = os.path.join(settings.MEDIA_ROOT, uploaded.name)
            
            print(f"Processing image: {uploaded.name}")
            print(f"Model path: {model_path}")
            print(f"Model classes: {model.names}")
            
            with open(input_path, "wb+") as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
            
            # Run detection with lower confidence threshold
            results = model(input_path, conf=0.4, iou=0.4, imgsz=640)
            
            # Save annotated result
            output_filename = f"result_{uploaded.name}"
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
            results[0].save(filename=output_path)
            
            # Check for detections
            detections = []
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    class_name = model.names[int(box.cls)]
                    confidence = float(box.conf)
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence
                    })
                    
                    # Log detection with alert flag for higher confidence
                    DetectionLog.objects.create(
                        detection_type=class_name.lower(),
                        confidence=confidence * 100,  # Convert to percentage
                        image_path=output_filename,
                        alert_sent=True if confidence > 0.2 else False
                    )
            
            return JsonResponse({
                "status": "success",
                "result_image": settings.MEDIA_URL + output_filename,
                "detections": detections
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error processing image: {str(e)}"
            })
    
    return render(request, "image_detect.html")

@login_required(login_url='login')
def video_stream(request):
    """Live video stream page"""
    return render(request, "video_stream.html")

def video_feed(request):
    """Video streaming generator"""
    def generate():
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Run YOLO detection
                results = model(frame, conf=0.15, iou=0.4, imgsz=640)
                annotated_frame = results[0].plot()
                
                # Check for detections
                if results[0].boxes is not None:
                    for box in results[0].boxes:
                        class_name = model.names[int(box.cls)]
                        confidence = float(box.conf)
                        
                        if confidence > 0.2:
                            DetectionLog.objects.create(
                                detection_type=class_name.lower(),
                                confidence=confidence * 100,  
                                alert_sent=confidence > 0.4
                            )
                
                # Encode frame
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
        except Exception as e:
            print(f"Video feed error: {e}")
        finally:
            if cap:
                cap.release()
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

@login_required(login_url='login')
def logs_view(request):
    """Detection logs page"""
    logs = DetectionLog.objects.all()[:50]
    return render(request, "logs.html", {"logs": logs})

@csrf_exempt
def api_stats(request):
    """API endpoint for dashboard stats"""
    recent_alerts = []
    for log in DetectionLog.objects.filter(alert_sent=True)[:5]:
        recent_alerts.append({
            'detection_type': log.detection_type,
            'confidence': log.confidence,
            'detected_at': log.detected_at.strftime('%Y-%m-%d %H:%M:%S'),
            'id': log.id
        })
    
    stats = {
        'total_detections': DetectionLog.objects.count(),
        'fire_detections': DetectionLog.objects.filter(detection_type='fire').count(),
        'smoke_detections': DetectionLog.objects.filter(detection_type='smoke').count(),
        'recent_alerts': recent_alerts,
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return JsonResponse(stats)

def export_logs_pdf(request):
    """Export detection logs to PDF"""
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    filename = f'fire_detection_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create the PDF object using ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40,
                          topMargin=40, bottomMargin=40)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff6b35'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Add title
    title = Paragraph("Fire Detection System - Detection Logs", title_style)
    elements.append(title)
    
    # Add timestamp
    timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", subtitle_style)
    elements.append(timestamp)
    elements.append(Spacer(1, 0.2*inch))
    
    # Get logs data
    logs = DetectionLog.objects.all()[:100]  # Limit to 100 most recent logs
    
    # Summary statistics
    total_logs = DetectionLog.objects.count()
    fire_count = DetectionLog.objects.filter(detection_type='fire').count()
    smoke_count = DetectionLog.objects.filter(detection_type='smoke').count()
    high_confidence = DetectionLog.objects.filter(confidence__gt=70).count()
    
    # Add summary section
    summary_data = [
        ['Summary Statistics', '', '', ''],
        ['Total Detections', str(total_logs), 'Fire Detections', str(fire_count)],
        ['Smoke Detections', str(smoke_count), 'High Confidence (>70%)', str(high_confidence)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Create table data for logs
    data = [['ID', 'Type', 'Confidence', 'Date & Time', 'Alert Sent']]
    
    for log in logs:
        data.append([
            str(log.id),
            log.get_detection_type_display(),
            f"{log.confidence:.1f}%",
            log.detected_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Yes' if log.alert_sent else 'No'
        ])
    
    # Create the table
    table = Table(data, colWidths=[0.6*inch, 1.2*inch, 1.2*inch, 2*inch, 1*inch])
    
    # Add style to table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # # Add footer note
    # elements.append(Spacer(1, 0.3*inch))
    # footer_text = Paragraph(
    #     f"<i>This report contains the most recent detection logs from the Fire Detection System.</i>",
    #     styles['Normal']
    # )
    # elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    """User logout view"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! Please login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})