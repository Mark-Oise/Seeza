from django.contrib.auth import get_user_model
from django.db import models
import uuid
from django.urls import reverse
from django.conf import settings
import markdown
from django.utils.safestring import mark_safe
import json
import re
from django.template.loader import render_to_string
import os
from PIL import Image
from io import BytesIO


# Create your models here.


class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=36, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('chat:conversation_detail', kwargs={'slug': self.slug})

    def rename_title(self, new_title):
        if new_title and new_title != self.title:
            self.title = new_title
            self.save()
        return self.title

    def toggle_archive(self):
        self.is_archived = not self.is_archived
        self.save()
        return self.is_archived

    def toggle_star(self):
        self.is_starred = not self.is_starred
        self.save()
        return self.is_starred

    def delete_conversation(self):
        self.is_deleted = True
        self.save()
        return self.is_deleted


class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    def get_content_as_markdown(self):
        def replace_code_block(match):
            language = match.group(1) or 'plaintext'
            code = match.group(2)
            return render_to_string('chat/partials/code_block.html', {
                'language': language,
                'code': code,
                'message_id': self.id,
                'block_id': f'code-{len(re.findall(r"```", self.content[:match.start()]))}',
            })

        # Replace code blocks with custom HTML
        content_with_custom_blocks = re.sub(r'```(\w+)?\n(.*?)\n```', replace_code_block, self.content, flags=re.DOTALL)

        # Convert the rest of the content to Markdown
        md = markdown.Markdown(extensions=['extra', 'nl2br', 'fenced_code', 'codehilite', 'sane_lists', 'attr_list'])
        return mark_safe(md.convert(content_with_custom_blocks))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Document(models.Model):
    message = models.ForeignKey(Message, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_documents/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ImageAttachment(models.Model):
    message = models.ForeignKey(Message, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='chat_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only process the image when first saving
            # Open the image using PIL
            img = Image.open(self.image)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions while maintaining aspect ratio
            max_size = 768
            ratio = min(max_size/float(img.size[0]), max_size/float(img.size[1]))
            new_size = tuple([int(x*ratio) for x in img.size])
            
            # Resize image
            if max(img.size) > max_size:
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save the processed image
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            self.image.save(
                os.path.splitext(self.image.name)[0] + '.jpg',
                buffer,
                save=False
            )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for message {self.message.id}"

    class Meta:
        ordering = ['created_at']