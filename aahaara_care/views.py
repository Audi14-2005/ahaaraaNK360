from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import models
import json
from .models import ChatSession, ChatMessage, MedicalKnowledgeBase, ChatFeedback
from .services import NKCareAI, MedicalQueryAnalyzer, PatientDataService


@login_required
def chat_dashboard(request):
    """Main chat dashboard for AAHAARA Care"""
    # Get recent chat sessions
    recent_sessions = ChatSession.objects.filter(
        doctor=request.user, 
        is_active=True
    )[:5]
    
    # Get statistics
    total_sessions = ChatSession.objects.filter(doctor=request.user).count()
    total_messages = ChatMessage.objects.filter(
        session__doctor=request.user
    ).count()
    
    # Get active session or create new one
    active_session = ChatSession.objects.filter(
        doctor=request.user, 
        is_active=True
    ).first()
    
    if not active_session:
        active_session = ChatSession.objects.create(
            doctor=request.user,
            title="New Chat Session"
        )
    
    context = {
        'recent_sessions': recent_sessions,
        'active_session': active_session,
        'total_sessions': total_sessions,
        'total_messages': total_messages,
    }
    return render(request, 'aahaara_care/chat_dashboard.html', context)


@login_required
def chat_session(request, session_id):
    """Individual chat session view"""
    session = get_object_or_404(ChatSession, id=session_id, doctor=request.user)
    
    # Get messages for this session
    messages = session.messages.all()
    
    # Paginate messages if there are many
    paginator = Paginator(messages, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'session': session,
        'messages': page_obj,
    }
    return render(request, 'aahaara_care/chat_session.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_message(request, session_id):
    """Send a message to AAHAARA Care and get response"""
    print(f"DEBUG: send_message called with session_id: {session_id}")
    print(f"DEBUG: User: {request.user}")
    print(f"DEBUG: Request body: {request.body}")
    
    try:
        session = get_object_or_404(ChatSession, id=session_id, doctor=request.user)
        print(f"DEBUG: Session found: {session}")
    except Exception as e:
        print(f"DEBUG: Session error: {e}")
        return JsonResponse({'error': 'Session not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        print(f"DEBUG: User message: {user_message}")
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Save user message
        print("DEBUG: Saving user message...")
        try:
            user_msg = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message
            )
            print(f"DEBUG: User message saved: {user_msg.id}")
        except Exception as e:
            print(f"DEBUG: User message save error: {e}")
            return JsonResponse({'error': f'Failed to save message: {str(e)}'}, status=500)
        
        # Analyze the query
        print("DEBUG: Creating query analyzer...")
        try:
            query_analyzer = MedicalQueryAnalyzer()
            query_analysis = query_analyzer.analyze_query(user_message)
            print(f"DEBUG: Query analysis: {query_analysis}")
        except Exception as e:
            print(f"DEBUG: Query analyzer error: {e}")
            query_analysis = {'primary_category': 'general', 'confidence': 0.5}
        
        # Get patient data if this is a patient query
        patient_data = None
        if query_analysis.get('is_patient_query'):
            print("DEBUG: Patient query detected, retrieving patient data...")
            try:
                patient_service = PatientDataService()
                patient_identifier = query_analysis.get('patient_identifier')
                patient_result = patient_service.get_patient_data(request.user, patient_identifier)
                print(f"DEBUG: Patient data result: {patient_result.get('found', False)}")
                
                if patient_result.get('found'):
                    # If specific patient requested, get that patient's data
                    if patient_identifier and patient_result.get('patients'):
                        # Find the matching patient
                        for patient_key, patient_info in patient_result['patients'].items():
                            if (patient_identifier.lower() in patient_key.lower() or 
                                patient_identifier.lower() in (patient_info.get('patient_name', '').lower()) or
                                patient_identifier.lower() in (patient_info.get('patient_id', '').lower())):
                                patient_data = patient_info
                                break
                    
                    # If no specific patient or not found, use first patient
                    if not patient_data and patient_result.get('patients'):
                        patient_data = list(patient_result['patients'].values())[0]
                else:
                    print(f"DEBUG: No patient data found: {patient_result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"DEBUG: Patient data retrieval error: {e}")
                patient_data = None
        
        # Get chat history for context
        print("DEBUG: Getting chat history...")
        try:
            # Get last 10 messages using proper Django syntax
            recent_messages = session.messages.order_by('timestamp')[:10]
            chat_history = []
            for msg in recent_messages:
                chat_history.append({
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                })
            print(f"DEBUG: Chat history retrieved: {len(chat_history)} messages")
        except Exception as e:
            print(f"DEBUG: Chat history error: {e}")
            chat_history = []
        
        # Generate AI response
        print("DEBUG: Creating AI service...")
        try:
            ai_service = NKCareAI()
            print("DEBUG: AI service created successfully")
        except Exception as e:
            print(f"DEBUG: AI service creation error: {e}")
            return JsonResponse({'error': f'AI service error: {str(e)}'}, status=500)
        
        print("DEBUG: Generating AI response...")
        try:
            ai_response = ai_service.generate_response(
                user_message, 
                chat_history, 
                query_analysis,
                patient_data
            )
            print(f"DEBUG: AI response generated: {ai_response.get('success', False)}")
        except Exception as ai_error:
            print(f"DEBUG: AI response error: {ai_error}")
            # Provide a fallback response
            ai_response = {
                'success': True,
                'response': f"I'm AAHAARA Care, your medical AI assistant. I'm currently experiencing technical difficulties, but I'm here to help with your medical query: '{user_message}'. Please consult with a medical professional for accurate diagnosis and treatment.",
                'confidence_score': 0.3,
                'medical_advice_flag': True,
                'safety_warnings': ['AI service temporarily unavailable'],
                'suggested_actions': ['Consult with a medical professional'],
                'ai_model': 'fallback'
            }
        
        if ai_response['success']:
            # Save AI response
            ai_msg = ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=ai_response['response'],
                medical_context=query_analysis,
                confidence_score=ai_response['confidence_score'],
                is_medical_advice=ai_response['medical_advice_flag']
            )
            
            # Update session timestamp
            session.save()
            
            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': str(user_msg.id),
                    'content': user_msg.content,
                    'timestamp': user_msg.timestamp.isoformat(),
                    'type': user_msg.message_type
                },
                'ai_response': {
                    'id': str(ai_msg.id),
                    'content': ai_msg.content,
                    'timestamp': ai_msg.timestamp.isoformat(),
                    'type': ai_msg.message_type,
                    'confidence_score': ai_msg.confidence_score,
                    'is_medical_advice': ai_msg.is_medical_advice,
                    'safety_warnings': ai_response.get('safety_warnings', []),
                    'suggested_actions': ai_response.get('suggested_actions', [])
                }
            })
        else:
            # Save error message
            error_msg = ChatMessage.objects.create(
                session=session,
                message_type='system',
                content=f"Error: {ai_response.get('error', 'Unknown error')}"
            )
            
            return JsonResponse({
                'success': False,
                'error': ai_response.get('error', 'Unknown error'),
                'user_message': {
                    'id': str(user_msg.id),
                    'content': user_msg.content,
                    'timestamp': user_msg.timestamp.isoformat(),
                    'type': user_msg.message_type
                }
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def create_new_session(request):
    """Create a new chat session"""
    session = ChatSession.objects.create(
        doctor=request.user,
        title="New Chat Session"
    )
    
    # Deactivate other sessions
    ChatSession.objects.filter(
        doctor=request.user, 
        is_active=True
    ).exclude(id=session.id).update(is_active=False)
    
    messages.success(request, 'New chat session created!')
    return redirect('aahaara_care:chat_session', session_id=session.id)


@login_required
def session_list(request):
    """List all chat sessions"""
    sessions = ChatSession.objects.filter(doctor=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        sessions = sessions.filter(
            title__icontains=search_query
        ) | sessions.filter(
            messages__content__icontains=search_query
        ).distinct()
    
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'sessions': page_obj,
        'search_query': search_query,
    }
    return render(request, 'aahaara_care/session_list.html', context)


@login_required
@require_http_methods(["POST"])
def submit_feedback(request, message_id):
    """Submit feedback for a chat message"""
    message = get_object_or_404(ChatMessage, id=message_id, session__doctor=request.user)
    
    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        is_helpful = data.get('is_helpful', True)
        
        if not rating or rating not in [1, 2, 3, 4, 5]:
            return JsonResponse({'error': 'Invalid rating'}, status=400)
        
        # Create or update feedback
        feedback, created = ChatFeedback.objects.get_or_create(
            message=message,
            doctor=request.user,
            defaults={
                'rating': rating,
                'feedback_text': feedback_text,
                'is_helpful': is_helpful
            }
        )
        
        if not created:
            feedback.rating = rating
            feedback.feedback_text = feedback_text
            feedback.is_helpful = is_helpful
            feedback.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def knowledge_base(request):
    """Medical knowledge base"""
    categories = MedicalKnowledgeBase.CATEGORIES
    selected_category = request.GET.get('category', '')
    
    knowledge_items = MedicalKnowledgeBase.objects.filter(is_active=True)
    
    if selected_category:
        knowledge_items = knowledge_items.filter(category=selected_category)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        knowledge_items = knowledge_items.filter(
            title__icontains=search_query
        ) | knowledge_items.filter(
            content__icontains=search_query
        )
    
    paginator = Paginator(knowledge_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'knowledge_items': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'aahaara_care/knowledge_base.html', context)


@login_required
def analytics(request):
    """Analytics for AAHAARA Care usage"""
    # Get user's chat statistics
    total_sessions = ChatSession.objects.filter(doctor=request.user).count()
    total_messages = ChatMessage.objects.filter(session__doctor=request.user).count()
    ai_messages = ChatMessage.objects.filter(
        session__doctor=request.user,
        message_type='assistant'
    ).count()

    # Get feedback statistics
    feedback_count = ChatFeedback.objects.filter(doctor=request.user).count()
    helpful_feedback_count = ChatFeedback.objects.filter(
        doctor=request.user, 
        is_helpful=True
    ).count()

    # Get recent activity
    recent_sessions = ChatSession.objects.filter(
        doctor=request.user
    ).order_by('-created_at')[:10]

    context = {
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'ai_messages': ai_messages,
        'feedback_count': feedback_count,
        'helpful_feedback_count': helpful_feedback_count,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'aahaara_care/analytics.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def edit_message(request, message_id):
    """Edit a chat message"""
    try:
        message = get_object_or_404(ChatMessage, id=message_id, session__doctor=request.user)
        
        # Only allow editing user messages, not AI responses
        if message.message_type != 'user':
            return JsonResponse({
                'success': False,
                'error': 'Only user messages can be edited'
            }, status=400)
        
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({
                'success': False,
                'error': 'Message content cannot be empty'
            }, status=400)
        
        # Update the message
        message.content = new_content
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message updated successfully',
            'updated_content': message.content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_message(request, message_id):
    """Delete a chat message"""
    try:
        message = get_object_or_404(ChatMessage, id=message_id, session__doctor=request.user)
        
        # Delete the message
        message.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Message deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_session(request, session_id):
    """Delete an entire chat session"""
    try:
        session = get_object_or_404(ChatSession, id=session_id, doctor=request.user)
        
        # Delete all messages in the session first
        session.messages.all().delete()
        
        # Delete the session
        session.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Chat session deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def bulk_delete_messages(request):
    """Delete multiple chat messages"""
    try:
        data = json.loads(request.body)
        message_ids = data.get('message_ids', [])
        
        if not message_ids:
            return JsonResponse({
                'success': False,
                'error': 'No messages selected'
            }, status=400)
        
        # Get messages that belong to the user
        messages = ChatMessage.objects.filter(
            id__in=message_ids,
            session__doctor=request.user
        )
        
        deleted_count = messages.count()
        messages.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} messages deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
