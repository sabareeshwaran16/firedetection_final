# 🔥 Fire Detection System - Modern UI

A beautiful, modern web interface for the fire detection YOLO system with smooth animations and transitions.

## ✨ Features

- **Modern Design**: Gradient backgrounds, glassmorphism effects, and smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Detection**: Live video stream with instant fire and smoke detection
- **Image Upload**: Drag & drop or click to upload images for detection
- **Beautiful Transitions**: Smooth fade-ins, hover effects, and loading animations
- **Dark Theme**: Eye-friendly dark mode with vibrant accent colors
- **Detection History**: View all past detections with confidence scores

## 🎨 UI Components

### Navigation
- Sticky navigation bar with blur effect
- Smooth scroll highlighting
- Gradient logo with fire emoji animation

### Dashboard
- Animated statistics cards with hover effects
- Quick action cards with icons
- Recent detections table
- Real-time counter animations

### Image Detection
- Drag & drop upload area
- Image preview with zoom animation
- Results display with confidence bars
- Detection badges with icons

### Live Stream
- Real-time video feed
- Session statistics
- Live alerts panel
- Stream controls

## 🚀 Installation & Setup

1. **Navigate to the detection folder**:
   ```powershell
   cd C:\Users\Dell\OneDrive\Desktop\projects\firedetection_final\firedetection_yolo\firedetection_yolo\detection
   ```

2. **Install Python dependencies** (if not already installed):
   ```powershell
   pip install django ultralytics opencv-python pillow
   ```

3. **Run migrations** (if needed):
   ```powershell
   python manage.py migrate
   ```

4. **Collect static files**:
   ```powershell
   python manage.py collectstatic --noinput
   ```

5. **Start the development server**:
   ```powershell
   python manage.py runserver
   ```

6. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

## 📁 File Structure

```
detection/
├── myapp/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Modern styles with animations
│   │   └── js/
│   │       └── main.js        # Interactive JavaScript functions
│   ├── templates/
│   │   ├── base.html          # Base template with navigation
│   │   ├── dashboard.html     # Main dashboard
│   │   ├── image_detect.html  # Image upload & detection
│   │   ├── video_stream.html  # Live video stream
│   │   └── logs.html          # Detection history
│   └── views.py               # Django views
├── detection/
│   └── settings.py            # Django settings
└── manage.py
```

## 🎨 CSS Features

- **CSS Variables**: Easy theme customization
- **Animations**: Fade-ins, slide-ins, zoom effects, pulse animations
- **Transitions**: Smooth hover effects and state changes
- **Responsive Grid**: Auto-adjusting layouts
- **Glassmorphism**: Backdrop blur effects
- **Gradient Backgrounds**: Dynamic color schemes

## 🔧 Customization

### Change Colors
Edit the CSS variables in `style.css`:

```css
:root {
    --primary-color: #ff6b35;      /* Main fire orange */
    --secondary-color: #f7931e;    /* Accent orange */
    --dark-color: #1a1a2e;         /* Background dark */
    --success-color: #00d9ff;      /* Success cyan */
}
```

### Add New Animations
All animations are defined in `style.css`:

```css
@keyframes yourAnimation {
    from { /* start state */ }
    to { /* end state */ }
}
```

## 📊 JavaScript Functions

Available in `FireDetection` global object:

- `initializeFileUpload(uploadAreaId, fileInputId, previewId)` - Setup drag & drop
- `detectImage(formId, resultsId)` - Handle image detection
- `startVideoStream(videoFeedUrl, containerId, statusId)` - Start video
- `stopVideoStream(containerId, statusId)` - Stop video
- `showAlert(message, type)` - Display notifications

## 🌟 Key Features

### Smooth Transitions
- All hover effects: 0.3s ease
- Card animations: fadeInUp, fadeInDown
- Loading states with spinners
- Confidence bar fill animations

### Responsive Design
- Mobile-first approach
- Grid layouts with auto-fit
- Breakpoints at 768px
- Touch-friendly buttons

### Accessibility
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- High contrast colors

## 📝 Notes

- The YOLO model file (`best.pt`) should be in the parent directory
- Camera permissions required for live stream
- Static files are served from `staticfiles/` in production

## 🐛 Troubleshooting

**Static files not loading?**
```powershell
python manage.py collectstatic --noinput
```

**Camera not working?**
- Check camera permissions in browser
- Ensure camera is not in use by another app

**Detection not working?**
- Verify `best.pt` model file exists
- Check ultralytics installation

## 📱 Browser Support

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

## 🎯 Performance

- Optimized animations with GPU acceleration
- Lazy loading for images
- Debounced scroll events
- Efficient CSS selectors

Enjoy your beautiful fire detection interface! 🔥
