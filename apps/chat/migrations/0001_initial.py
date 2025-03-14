# Generated by Django 4.2.14 on 2024-09-16 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Conversation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256)),
                ("slug", models.SlugField(editable=False, max_length=36, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("session_key", models.CharField(blank=True, max_length=40, null=True)),
                ("is_archived", models.BooleanField(default=False)),
                ("is_starred", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sender",
                    models.CharField(
                        choices=[("user", "User"), ("bot", "Bot")], max_length=10
                    ),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chat.conversation",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="chat_documents/")),
                ("filename", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="chat.message",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(fields=["user"], name="chat_conver_user_id_54eba5_idx"),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["session_key"], name="chat_conver_session_a04e96_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["created_at"], name="chat_conver_created_656b50_idx"
            ),
        ),
    ]
