from .models import Conversation


def conversations(request):
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(user=request.user, is_deleted=False).order_by('-updated_at')
    else:
        session_key = request.session.session_key or request.session.create()
        conversations = Conversation.objects.filter(session_key=session_key, is_deleted=False).order_by('-updated_at')

    return {'conversations': conversations}
