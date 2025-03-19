from ..models import ImageAttachment, Message
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from channels.db import database_sync_to_async
import os

class ImageService:
    """Service for handling image uploads and processing."""
    
    def __init__(self):
        """Initialize the image service."""
        pass
    
    @database_sync_to_async
    def attach_temp_images_to_message(self, message, temp_images):
        """
        Attach temporarily uploaded images to a message.
        
        Args:
            message: Message object to attach images to
            temp_images: List of temporary image data from session
        
        Returns:
            List of created ImageAttachment objects
        """
        return self.attach_temp_images_to_message_sync(message, temp_images)
    
    def attach_temp_images_to_message_sync(self, message, temp_images):
        """
        Synchronous version of attach_temp_images_to_message.
        """
        attachments = []
        
        for image_data in temp_images:
            # Read the temporary file
            temp_path = image_data['path']
            file_content = default_storage.open(temp_path).read()
            
            # Create image attachment
            image_attachment = ImageAttachment(message=message)
            
            # Save the image to its permanent location
            filename = os.path.basename(image_data['filename'])
            image_attachment.image.save(filename, ContentFile(file_content))
            image_attachment.save()
            
            # Delete the temporary file
            default_storage.delete(temp_path)
            
            attachments.append(image_attachment)
            
        return attachments
    
    @staticmethod
    def clean_temp_images_from_session(request):
        """
        Clean up temporary images from the session.
        
        Args:
            request: The HTTP request object containing the session
            
        Returns:
            Boolean indicating if any images were cleaned
        """
        if 'temp_images' not in request.session:
            return False
            
        # Clean up any temp files stored
        for image_data in request.session.get('temp_images', []):
            if 'path' in image_data:
                default_storage.delete(image_data['path'])
                
        # Remove from session
        request.session.pop('temp_images', None)
        request.session.modified = True
        return True
    
    @staticmethod
    def process_temp_images_for_message(request, message):
        """
        Process and attach any temporary images for a message, then clean up.
        
        Args:
            request: The HTTP request object
            message: The message to attach images to
            
        Returns:
            List of created attachments or None if no images
        """
        temp_images = request.session.get('temp_images', [])
        if not temp_images:
            return None
            
        # Process the images
        image_service = ImageService()
        attachments = image_service.attach_temp_images_to_message_sync(message, temp_images)
        
        # Clean up
        request.session.pop('temp_images', None)
        request.session.modified = True
        
        return attachments
    
    @database_sync_to_async
    def get_message_images(self, message_id):
        """Get all images attached to a message."""
        message = Message.objects.get(id=message_id)
        return list(message.images.all())
