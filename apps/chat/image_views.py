import os
import uuid
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render

def upload_image(request):
    """
    Handle HTMX image upload requests.
    Returns updated attachment container with new image.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif']
        if image.content_type not in allowed_types:
            return HttpResponse("Invalid file type. Please upload an image.", status=400)
        
        # Generate a unique filename for temporary storage
        file_extension = os.path.splitext(image.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Store in temporary location using Django's storage
        temp_path = f"temp_uploads/{unique_filename}"
        path = default_storage.save(temp_path, ContentFile(image.read()))
        temp_file_url = default_storage.url(path)
        
        # Store image info in session for later association with a message
        if 'temp_images' not in request.session:
            request.session['temp_images'] = []
        
        image_data = {
            'id': str(uuid.uuid4()),
            'filename': image.name,
            'path': temp_path,
            'url': temp_file_url
        }
        request.session['temp_images'].append(image_data)
        request.session.modified = True
        
        # Get all temp images to render the full attachment container
        temp_images = request.session.get('temp_images', [])
        
        # Return the updated attachment container
        return render(request, 'chat/attachments/attachment.html', {
            'temp_images': temp_images
        })
    
    return HttpResponse("No image provided", status=400)

def remove_image(request, image_id):
    """
    Remove a temporarily uploaded image.
    """
    if request.method == 'POST' and 'temp_images' in request.session:
        temp_images = request.session['temp_images']
        
        for i, image_data in enumerate(temp_images):
            if image_data['id'] == image_id:
                # Remove the file from storage
                default_storage.delete(image_data['path'])
                # Remove from session
                temp_images.pop(i)
                request.session.modified = True
                break
        
        # If there are no more images, return empty container
        if not temp_images:
            return render(request, 'chat/attachments/attachment.html', {
                'temp_images': []
            })
        
        # Return blank response since the image was removed via htmx
        return HttpResponse("")
    
    return HttpResponse("Image not found", status=404)


    """
    Remove a temporarily uploaded image.
    """
    if request.method == 'POST' and 'temp_images' in request.session:
        temp_images = request.session['temp_images']
        
        for i, image_data in enumerate(temp_images):
            if image_data['id'] == image_id:
                # Remove the file from storage
                default_storage.delete(image_data['path'])
                # Remove from session
                temp_images.pop(i)
                request.session.modified = True
                break
        
        return HttpResponse("Image removed")
    
    return HttpResponse("Image not found", status=404)