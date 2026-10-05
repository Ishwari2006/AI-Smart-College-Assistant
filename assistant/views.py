from datetime import datetime, timedelta
import os
import re
import difflib
import pandas as pd
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from google import genai
from dotenv import load_dotenv

from .models import FAQ, Notice, Assignment, Timetable, UserProfile
from .forms import NoticeForm, AssignmentForm, TimetableForm, FAQForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

load_dotenv()
load_dotenv()


# =========================================================
# PUBLIC HOME PAGE
# =========================================================

def landing_page(request):
    return render(
        request,
        'assistant/index.html'
    )


# =========================================================
# HOME / STUDENT DASHBOARD
# =========================================================

@login_required
def home(request):

    # Staff user should go to Staff Dashboard
    try:
        if request.user.userprofile.role == 'staff':
            return redirect('staff_dashboard')
    except UserProfile.DoesNotExist:
        pass

    today = datetime.now().strftime('%A')

    today_timetable = Timetable.objects.filter(
        day__iexact=today,
        timetable_type='student'
    ).order_by('start_time')

    latest_notices = Notice.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')[:3]

    return render(
        request,
        'assistant/dashboard.html',
        {
            'today_timetable': today_timetable,
            'latest_notices': latest_notices
        }
    )

# =========================================================
# HOME / STUDENT DASHBOARD
# =========================================================

@login_required
def home(request):

    # Staff user should go to Staff Dashboard
    try:
        if request.user.userprofile.role == 'staff':
            return redirect('staff_dashboard')
    except UserProfile.DoesNotExist:
        pass

    today = datetime.now().strftime('%A')

    today_timetable = Timetable.objects.filter(
        day__iexact=today,
        timetable_type='student'
    ).order_by('start_time')

    latest_notices = Notice.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')[:3]

    return render(
        request,
        'assistant/dashboard.html',
        {
            'today_timetable': today_timetable,
            'latest_notices': latest_notices
        }
    )
def landing_page(request):
    user_count = User.objects.filter(
        is_active=True
    ).count()

    return render(
        request,
        'assistant/index.html',
        {
            'user_count': user_count
        }
    )
# =========================================================
# NOTICES PAGE
# =========================================================

@login_required
def notices(request):

    notices = Notice.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')

    return render(
        request,
        'assistant/notices.html',
        {
            'notices': notices
        }
    )


# =========================================================
# ASSIGNMENTS PAGE
# =========================================================

@login_required
def assignments(request):

    assignments = Assignment.objects.filter(
        due_date__gte=timezone.now().date()
    ).order_by('due_date')

    return render(
        request,
        'assistant/assignments.html',
        {
            'assignments': assignments
        }
    )


# =========================================================
# TIMETABLE PAGE
# =========================================================

@login_required
def timetable(request):

    day_order = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }

    timetable_data = list(
        Timetable.objects.filter(
            timetable_type='student'
        )
    )

    for item in timetable_data:
        item.day = item.day.strip().capitalize()

    timetable_data.sort(
        key=lambda x: (
            day_order.get(x.day, 99),
            x.start_time
        )
    )

    return render(
        request,
        'assistant/timetable.html',
        {
            'timetable': timetable_data
        }
    )


# =========================================================
# FAQ PAGE
# =========================================================

@login_required
def faq(request):

    faqs = FAQ.objects.all()

    return render(
        request,
        'assistant/faq.html',
        {
            'faqs': faqs
        }
    )


# =========================================================
# CHATBOT PAGE
# =========================================================

@login_required
def chatbot(request):

    return render(
        request,
        'assistant/chatbot.html'
    )


# =========================================================
# CHATBOT RESPONSE
# =========================================================

@login_required
def chatbot_response(request):

    message = request.GET.get('message', '').strip()

    # -----------------------------------------------------
    # EMPTY MESSAGE
    # -----------------------------------------------------

    if not message:
        return JsonResponse({
            'response': 'Please ask me a question.'
        })

    message_lower = message.lower()

    # -----------------------------------------------------
    # SPELLING CORRECTION
    # -----------------------------------------------------

    correct_words = [
        "schedule",
        "timetable",
        "today",
        "tomorrow",
        "assignment",
        "assignments",
        "pending",
        "remaining",
        "notice",
        "notices",
        "class",
        "classes",
        "subject",
        "subjects",
        "college",
        "timing",
        "time",
        "faq",
        "fees",
        "exam",
        "exams",
        "admission",
        "library",
        "attendance",
        "teacher",
        "teachers",
        "faculty",
        "department"
    ]

    words = message_lower.split()
    corrected_words = []

    for word in words:

        clean_word = re.sub(
            r'[^a-z0-9]',
            '',
            word
        )

        if clean_word:

            match = difflib.get_close_matches(
                clean_word,
                correct_words,
                n=1,
                cutoff=0.75
            )

            if match:
                corrected_words.append(match[0])
            else:
                corrected_words.append(word)

        else:
            corrected_words.append(word)

    message_lower = " ".join(corrected_words)

    # Common phrases
    message_lower = message_lower.replace(
        "time table",
        "timetable"
    )

    message_lower = message_lower.replace(
        "today s",
        "today"
    )

    # -----------------------------------------------------
    # GEMINI CLIENT
    # -----------------------------------------------------

    try:

        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    except Exception as e:

        print("Gemini Client Error:", e)

        client = None

    # -----------------------------------------------------
    # LANGUAGE DETECTION
    # -----------------------------------------------------

    original_language = "English"
    english_query = message_lower

    if re.search(r'[\u0900-\u097F]', message):

        if client:

            try:

                language_prompt = f"""
Identify the language of this student's question.

Possible languages:
- Marathi
- Hindi
- English

Also convert the question into simple English for searching
an English college FAQ database.

Return ONLY in this exact format:

LANGUAGE: Marathi
QUERY: What is the college timing?

OR

LANGUAGE: Hindi
QUERY: What is the college timing?

OR

LANGUAGE: English
QUERY: What is the college timing?

Student question:
{message}
"""

                language_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=language_prompt
                )

                language_text = (
                    language_response.text.strip()
                )

                language_match = re.search(
                    r'LANGUAGE:\s*(Marathi|Hindi|English)',
                    language_text,
                    re.IGNORECASE
                )

                query_match = re.search(
                    r'QUERY:\s*(.*)',
                    language_text,
                    re.IGNORECASE
                )

                if language_match:

                    original_language = (
                        language_match.group(1).capitalize()
                    )

                if query_match:

                    english_query = (
                        query_match.group(1).strip()
                    )

            except Exception as e:

                print(
                    "Language Detection Error:",
                    e
                )

    english_query_lower = english_query.lower()

    # =====================================================
    # TEXT NORMALIZATION
    # =====================================================

    def normalize_text(text):

        text = text.lower()

        text = re.sub(
            r'[^\w\s]',
            ' ',
            text,
            flags=re.UNICODE
        )

        text = re.sub(
            r'\s+',
            ' ',
            text
        ).strip()

        return text

    def get_words(text):

        normalized = normalize_text(text)

        return set(normalized.split())

    # =====================================================
    # COMMON WORDS
    # =====================================================

    common_words = {
        'what', 'is', 'the', 'a', 'an', 'are', 'of', 'to', 'for',
        'in', 'on', 'when', 'where', 'how', 'can', 'i', 'do', 'does',
        'my', 'please', 'tell', 'me', 'about', 'give', 'show', 'this',
        'that', 'and', 'or', 'with', 'from', 'which', 'could', 'would',
        'there', 'be'
    }

    message_words = get_words(english_query)

    message_keywords = message_words - common_words

    # =====================================================
    # TODAY / YESTERDAY / TOMORROW ASSIGNMENTS
    # =====================================================

    if (
        ('assignment' in english_query_lower
         or 'assignments' in english_query_lower)
        and (
            'today' in english_query_lower
            or 'yesterday' in english_query_lower
            or 'tomorrow' in english_query_lower
        )
    ):

        if 'today' in english_query_lower:
            target_date = timezone.localdate()
            title = "📚 Today's Assignments"

        elif 'yesterday' in english_query_lower:
            target_date = timezone.localdate() - timedelta(days=1)
            title = "📚 Yesterday's Assignments"

        else:
            target_date = timezone.localdate() + timedelta(days=1)
            title = "📚 Tomorrow's Assignments"

        assignments_data = Assignment.objects.filter(
            due_date=target_date
        ).order_by('due_date', 'id')

        if assignments_data.exists():

            response_text = f"{title}:\n\n"

            for assignment in assignments_data:
                response_text += (
                    f"• {assignment.title} "
                    f"({assignment.subject}) - "
                    f"Due: {assignment.due_date.strftime('%d-%m-%Y')}\n"
                )

        else:
            response_text = (
                f"{title}\n\n"
                f"❌ No assignments are due on "
                f"{target_date.strftime('%d-%m-%Y')}."
            )

        # Translation for Marathi / Hindi
        if original_language != "English" and client:
            try:
                translate_prompt = f"""
Translate the following college assistant response into {original_language}.
Keep assignment titles, subject names and dates unchanged.
Use simple student-friendly language.
Return only the translated answer.

Response:
{response_text}
"""
                translated = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=translate_prompt
                )
                if translated.text:
                    response_text = translated.text.strip()
            except Exception as e:
                print("Date Assignment Translation Error:", e)

        return JsonResponse({'response': response_text})


    # =====================================================
    # 1. SPECIFIC ASSIGNMENT SEARCH
    # =====================================================
    # These words indicate that the student is asking for
    # a particular assignment/practical/task.
    specific_assignment_words = {
        'assignment',
        'assignments',
        'practical',
        'practicals',
        'homework',
        'task',
        'tasks'
    }

    # These words indicate a list/status query, which should
    # be handled by the Pending Assignments section below.
    pending_assignment_words = {
        'pending',
        'remaining',
        'due',
        'deadline'
    }

    query_word_set = set(
        normalize_text(english_query).split()
    )

    is_specific_assignment_query = (
        bool(
            query_word_set.intersection(
                specific_assignment_words
            )
        )
        and not bool(
            query_word_set.intersection(
                pending_assignment_words
            )
        )
    )

    if is_specific_assignment_query:

        combined_query = f"{message} {english_query}"
        normalized_query = normalize_text(combined_query)
        query_words = set(normalized_query.split())

        assignment_common_words = {
            'assignment',
            'assignments',
            'practical',
            'practicals',
            'homework',
            'work',
            'task',
            'tasks',
            'due',
            'date',
            'deadline',
            'information',
            'details',
            'tell',
            'about',
            'what',
            'is',
            'the',
            'my',
            'please',
            'give',
            'show',
            'when',
            'for',
            'of',
            'to',
            'me'
        }

        meaningful_query_words = (
            query_words - assignment_common_words
        )

        assignments_data = Assignment.objects.all().order_by(
            'due_date'
        )

        matched_assignment = None
        best_assignment_score = 0

        for assignment in assignments_data:

            normalized_title = normalize_text(
                assignment.title
            )

            normalized_subject = normalize_text(
                assignment.subject
            )

            title_words = set(
                normalized_title.split()
            )

            subject_words = set(
                normalized_subject.split()
            )

            meaningful_title_words = (
                title_words - assignment_common_words
            )

            meaningful_subject_words = (
                subject_words - assignment_common_words
            )

            # Exact complete title match
            if (
                normalized_title
                and normalized_title in normalized_query
            ):

                score = 100

            else:

                # Match meaningful title words
                title_matches = (
                    meaningful_query_words
                    .intersection(
                        meaningful_title_words
                    )
                )

                title_score = (
                    len(title_matches)
                    / max(
                        1,
                        len(meaningful_title_words)
                    )
                )

                # Match meaningful subject words
                subject_matches = (
                    meaningful_query_words
                    .intersection(
                        meaningful_subject_words
                    )
                )

                subject_score = (
                    len(subject_matches)
                    / max(
                        1,
                        len(meaningful_subject_words)
                    )
                )

                # Fuzzy title matching
                fuzzy_score = difflib.SequenceMatcher(
                    None,
                    normalized_query,
                    normalized_title
                ).ratio()

                # Title gets more importance than subject
                score = max(
                    title_score * 10,
                    subject_score * 3,
                    fuzzy_score * 2
                )

            if score > best_assignment_score:

                best_assignment_score = score
                matched_assignment = assignment

        # Return an assignment only when the match is strong
        if (
            matched_assignment
            and (
                best_assignment_score >= 5
                or best_assignment_score == 100
            )
        ):

            response_text = (
                "📚 Assignment Information:\n\n"
                f"Title: {matched_assignment.title}\n"
                f"Subject: {matched_assignment.subject}\n"
                f"Description: {matched_assignment.description}\n"
                f"Due Date: "
                f"{matched_assignment.due_date.strftime('%d-%m-%Y')}"
            )

            # Translation
            if (
                original_language != "English"
                and client
            ):

                try:

                    translate_prompt = f"""
Translate the following college assistant response into
{original_language}.

Important:
- Keep assignment title unchanged.
- Keep subject name unchanged.
- Keep description meaning unchanged.
- Keep date unchanged.
- Use simple student-friendly language.
- Return only the translated answer.

Response:
{response_text}
"""

                    translated = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=translate_prompt
                    )

                    if translated.text:

                        response_text = (
                            translated.text.strip()
                        )

                except Exception as e:

                    print(
                        "Assignment Translation Error:",
                        e
                    )

            return JsonResponse({
                'response': response_text
            })

    # =====================================================
    # 1. PENDING ASSIGNMENTS
    # =====================================================

    if (
        'assignment' in english_query_lower
        and (
            'pending' in english_query_lower
            or 'due' in english_query_lower
            or 'remaining' in english_query_lower
        )
    ):

        today = timezone.now().date()

        pending_assignments = Assignment.objects.filter(
            due_date__gte=today
        ).order_by('due_date')

        if pending_assignments.exists():

            response_text = "📚 Pending Assignments:\n\n"

            for assignment in pending_assignments:

                response_text += (
                    f"• {assignment.title} "
                    f"({assignment.subject}) - "
                    f"Due: {assignment.due_date}\n"
                )

        else:

            response_text = (
                "You have no pending assignments."
            )

        # Translation
        if (
            original_language != "English"
            and client
        ):

            try:

                translate_prompt = f"""
Translate the following college assistant response into
{original_language}.

Keep the meaning exactly the same.
Keep subject names, assignment names and dates unchanged.
Use simple student-friendly language.

Response:
{response_text}
"""

                translated = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=translate_prompt
                )

                response_text = translated.text.strip()

            except Exception as e:

                print(
                    "Translation Error:",
                    e
                )

        return JsonResponse({
            'response': response_text
        })

      # =====================================================
    # 3. TODAY'S / TOMORROW'S TIMETABLE
    # =====================================================

    if (
        (
            'timetable' in english_query_lower
            or 'schedule' in english_query_lower
        )
        and (
            'today' in english_query_lower
            or 'now' in english_query_lower
            or 'tomorrow' in english_query_lower
        )
    ):
        if 'tomorrow' in english_query_lower:
            target_day = (
                timezone.localdate() + timedelta(days=1)
            ).strftime('%A')
            title = "📅 Tomorrow's Timetable"
        else:
            target_day = timezone.localdate().strftime('%A')
            title = "📅 Today's Timetable"

        print("TARGET DAY FROM DJANGO:", target_day)

        print(
            "TIMETABLE FROM DATABASE:",
            list(
                Timetable.objects.filter(
                    day__iexact=target_day,
                    timetable_type='student'
                ).values(
                    'subject',
                    'start_time',
                    'end_time'
                )
            )
        )

        timetable_data = Timetable.objects.filter(
            day__iexact=target_day,
            timetable_type='student'
        ).order_by('start_time')

        if timetable_data.exists():

            response_text = (
                f"{title} ({target_day}):\n\n"
            )

            for item in timetable_data:

                response_text += (
                    f"• {item.subject} - "
                    f"{item.start_time.strftime('%H:%M')} to "
                    f"{item.end_time.strftime('%H:%M')}\n"
                )

        else:
            response_text = (
                f"📅 No timetable found for {target_day}."
            )

        return JsonResponse({
            'response': response_text
        })

    query_words = set(english_query_lower.split())

    english_timing_keywords = {
        'timing',
        'time',
        'start',
        'starts',
        'started',
        'end',
        'ends',
        'open',
        'close',
        'opening',
        'closing'
    }

    roman_marathi_timing_keywords = {
        'kadhi',
        'suru',
        'surute',
        'chalu',
        'band',
        'sut',
        'sutte',
        'vajta',
        'vaje'
    }

    roman_marathi_words = {
        'cha',
        'chi',
        'che',
        'kiti',
        'kadhi',
        'kay',
        'suru',
        'surute',
        'chalu',
        'band',
        'sut',
        'sutte',
        'vajta',
        'vaje',
        'ahe',
        'aahe'
    }

    has_college = 'college' in query_words

    has_timing_word = bool(
        query_words.intersection(english_timing_keywords)
        or query_words.intersection(roman_marathi_timing_keywords)
    )

    is_roman_marathi = bool(
        query_words.intersection(roman_marathi_words)
    )

    if has_college and has_timing_word:

        if is_roman_marathi:
            response_text = (
                "🏫 College Timing:\n\n"
                "College chi timing 10:30 AM te 5:30 PM ahe."
            )
        else:
            response_text = (
                "🏫 College Timing:\n\n"
                "The college timing is from 10:30 AM to 5:30 PM."
            )

        return JsonResponse({
            'response': response_text
        })

    # =====================================================
    # 4. COLLEGE NOTICES
    # =====================================================

    if (
        'notice' in english_query_lower
        or 'notices' in english_query_lower
    ):

        latest_notices = Notice.objects.filter(
            date__gte=timezone.now().date()
        ).order_by('date')

        if latest_notices.exists():

            response_text = (
                "📢 Latest College Notices:\n\n"
            )

            for notice in latest_notices[:5]:

                response_text += (
                    f"• {notice.title}\n"
                    f"  {notice.description}\n"
                    f"  Date: {notice.date}\n\n"
                )

        else:

            response_text = (
                "No current college notices are available."
            )

        # Translation
        if (
            original_language != "English"
            and client
        ):

            try:

                translate_prompt = f"""
Translate the following college assistant response into
{original_language}.

Keep notice titles, descriptions and dates unchanged.
Use simple student-friendly language.

Response:
{response_text}
"""

                translated = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=translate_prompt
                )

                response_text = translated.text.strip()

            except Exception as e:

                print(
                    "Translation Error:",
                    e
                )

        return JsonResponse({
            'response': response_text
        })

    # =====================================================
    # 5. FAQ DATABASE SEARCH
    # =====================================================

    faqs = FAQ.objects.all()

    best_faq = None
    best_score = 0

    for faq_item in faqs:

        question_words = get_words(
            faq_item.question
        )

        question_keywords = (
            question_words - common_words
        )

        if not message_keywords:
            continue

        matched_words = (
            message_keywords.intersection(
                question_keywords
            )
        )

        score = (
            len(matched_words)
            / len(message_keywords)
        )

        if score > best_score:

            best_score = score
            best_faq = faq_item

    # -----------------------------------------------------
    # FAQ MATCH FOUND
    # -----------------------------------------------------

    if (
        best_faq
        and best_score >= 0.5
    ):

        response_text = best_faq.answer

        if (
            original_language != "English"
            and client
        ):

            try:

                translate_prompt = f"""
You are an AI Smart College Assistant.

Translate the following English college information
into {original_language}.

Important:
- Keep the information exactly the same.
- Do not add new information.
- Do not remove any information.
- Keep names, numbers, dates and times unchanged.
- Use simple student-friendly language.
- Return only the translated answer.

English answer:
{response_text}
"""

                translated = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=translate_prompt
                )

                response_text = translated.text.strip()

            except Exception as e:

                print(
                    "FAQ Translation Error:",
                    e
                )

        return JsonResponse({
            'response': response_text
        })

    # =====================================================
    # 6. GEMINI AI FALLBACK
    # =====================================================

    if client:

        try:

            prompt = f"""
You are an AI Smart College Assistant.

Answer the student's question clearly and helpfully.

Important:
- Detect the language of the student's question.
- Support English, Marathi, and Hindi.
- Reply in the SAME language as the student's question.
- If the student uses Marathi mixed with English,
  reply naturally in Marathi-English mixed style.
- If the student uses Hindi mixed with English,
  reply naturally in Hindi-English mixed style.
- Keep the response simple and student-friendly.
- Do not invent college-specific information.
- If the required college information is not available
  in the database, politely say that the information is
  not available.

Student question:
{message}
"""

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            return JsonResponse({
                'response': response.text
            })

        except Exception as e:

            print(
                "Gemini Error:",
                e
            )

    # =====================================================
    # FINAL FALLBACK
    # =====================================================

    return JsonResponse({
        'response':
        'Sorry, I am unable to process your question right now.'
    })

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            return render(
                request,
                assistant/student_register.html,
                {
                    'error': 'Please fill all fields.'
                }
            )

        if password != confirm_password:
            return render(
                request,
                assistant/student_register.html,
                {
                    'error': 'Passwords do not match.'
                }
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'assistant/student_register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role='student'
        )

        return redirect('login')

    return render(
        request,
        'assistant/student_register.html'
    )
# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            return render(
                request,
                'assistant/student_register.html',
                {
                    'error': 'Please fill all fields.'
                }
            )

        if password != confirm_password:
            return render(
                request,
                'assistant/student_register.html',
                {
                    'error': 'Passwords do not match.'
                }
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'assistant/student_register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role='student'
        )

        return redirect('login')

    return render(
        request,
        'assistant/student_register.html'
    )


# =========================================================
# USER LOGIN
# =========================================================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Staff login
            try:
                if user.userprofile.role == 'staff':
                    return redirect('staff_dashboard')

            except UserProfile.DoesNotExist:
                pass

            # Student login
            return redirect('dashboard')

        return render(
            request,
            'assistant/login.html',
            {
                'error':
                'Invalid username or password.'
            }
        )

    return render(
        request,
        'assistant/login.html'
    )
# =========================================================
# USER LOGIN
# =========================================================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Staff login
            try:

                if user.userprofile.role == 'staff':
                    return redirect('staff_dashboard')

            except UserProfile.DoesNotExist:
                pass

            # Student login
            return redirect('dashboard')

        return render(
            request,
            'assistant/login.html',
            {
                'error':
                'Invalid username or password.'
            }
        )

    return render(
        request,
        'assistant/login.html'
    )


# =========================================================
# LOGOUT
# =========================================================

def user_logout(request):

    logout(request)

    return redirect('/')


# =========================================================
# STAFF ACCESS CHECK
# =========================================================

def is_staff_user(user):

    if not user.is_authenticated:
        return False

    try:

        return user.userprofile.role == 'staff'

    except UserProfile.DoesNotExist:

        return False


# =========================================================
# STAFF DASHBOARD
# =========================================================

@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    context = {
        'notice_count': Notice.objects.count(),
        'assignment_count': Assignment.objects.count(),
        'timetable_count': Timetable.objects.filter(
            timetable_type='staff'
        ).count(),
        'faq_count': FAQ.objects.count(),
    }

    return render(
        request,
        'assistant/staff_dashboard.html',
        context
    )
# =========================================================
# STAFF - NOTICES
# =========================================================

@login_required
@user_passes_test(is_staff_user)
def staff_notices(request):

    notices = Notice.objects.all().order_by('-date')

    return render(
        request,
        'assistant/staff_notices.html',
        {
            'notices': notices
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_notice_add(request):

    if request.method == 'POST':

        form = NoticeForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('staff_notices')

    else:

        form = NoticeForm()

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Add Notice'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_notice_edit(request, id):

    notice = get_object_or_404(
        Notice,
        id=id
    )

    if request.method == 'POST':

        form = NoticeForm(
            request.POST,
            instance=notice
        )

        if form.is_valid():

            form.save()

            return redirect('staff_notices')

    else:

        form = NoticeForm(
            instance=notice
        )

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Edit Notice'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_notice_delete(request, id):

    notice = get_object_or_404(
        Notice,
        id=id
    )

    if request.method == 'POST':

        notice.delete()

        return redirect('staff_notices')

    return render(
        request,
        'assistant/staff_confirm_delete.html',
        {
            'object': notice,
            'title': 'Delete Notice'
        }
    )


# =========================================================
# STAFF - ASSIGNMENTS
# =========================================================

@login_required
@user_passes_test(is_staff_user)
def staff_assignments(request):

    assignments = Assignment.objects.all().order_by(
        'due_date'
    )

    return render(
        request,
        'assistant/staff_assignments.html',
        {
            'assignments': assignments
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_assignment_add(request):

    if request.method == 'POST':

        form = AssignmentForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('staff_assignments')

    else:

        form = AssignmentForm()

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Add Assignment'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_assignment_edit(request, id):

    assignment = get_object_or_404(
        Assignment,
        id=id
    )

    if request.method == 'POST':

        form = AssignmentForm(
            request.POST,
            instance=assignment
        )

        if form.is_valid():

            form.save()

            return redirect('staff_assignments')

    else:

        form = AssignmentForm(
            instance=assignment
        )

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Edit Assignment'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_assignment_delete(request, id):

    assignment = get_object_or_404(
        Assignment,
        id=id
    )

    if request.method == 'POST':

        assignment.delete()

        return redirect('staff_assignments')

    return render(
        request,
        'assistant/staff_confirm_delete.html',
        {
            'object': assignment,
            'title': 'Delete Assignment'
        }
    )


# =========================================================
# STAFF - TIMETABLE
# =========================================================

# Staff Timetable

@login_required
@user_passes_test(is_staff_user)
def staff_timetable(request):
    timetables = Timetable.objects.filter(
        timetable_type='staff'
    ).order_by('day', 'start_time')

    return render(
        request,
        'assistant/staff_timetable.html',
        {'timetables': timetables}
    )


@login_required
@user_passes_test(is_staff_user)
def staff_timetable_add(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)

        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.timetable_type = 'staff'
            timetable.save()

            return redirect('staff_timetable')

    else:
        form = TimetableForm()

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Add Staff Timetable'
        }
    )

@login_required
@user_passes_test(is_staff_user)
def staff_timetable_edit(request, id):

    timetable_item = get_object_or_404(
        Timetable,
        id=id,
        timetable_type='staff'
    )

    if request.method == 'POST':

        form = TimetableForm(
            request.POST,
            instance=timetable_item
        )

        if form.is_valid():

            form.save()

            return redirect('staff_timetable')

    else:

        form = TimetableForm(
            instance=timetable_item
        )

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Edit Staff Timetable'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_timetable_delete(request, id):

    timetable_item = get_object_or_404(
        Timetable,
        id=id,
        timetable_type='staff'
    )

    if request.method == 'POST':

        timetable_item.delete()

        return redirect('staff_timetable')

    return render(
        request,
        'assistant/staff_confirm_delete.html',
        {
            'object': timetable_item,
            'title': 'Delete Staff Timetable'
        }
    )

# =========================================================
# STAFF - FAQ
# =========================================================

@login_required
@user_passes_test(is_staff_user)
def staff_faq(request):

    faqs = FAQ.objects.all().order_by(
        'question'
    )

    return render(
        request,
        'assistant/staff_faq.html',
        {
            'faqs': faqs
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_faq_add(request):

    if request.method == 'POST':

        form = FAQForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('staff_faq')

    else:

        form = FAQForm()

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Add FAQ'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_faq_edit(request, id):

    faq_item = get_object_or_404(
        FAQ,
        id=id
    )

    if request.method == 'POST':

        form = FAQForm(
            request.POST,
            instance=faq_item
        )

        if form.is_valid():

            form.save()

            return redirect('staff_faq')

    else:

        form = FAQForm(
            instance=faq_item
        )

    return render(
        request,
        'assistant/staff_form.html',
        {
            'form': form,
            'title': 'Edit FAQ'
        }
    )


@login_required
@user_passes_test(is_staff_user)
def staff_faq_delete(request, id):

    faq_item = get_object_or_404(
        FAQ,
        id=id
    )

    if request.method == 'POST':

        faq_item.delete()

        return redirect('staff_faq')

    return render(
        request,
        'assistant/staff_confirm_delete.html',
        {
            'object': faq_item,
            'title': 'Delete FAQ'
        }
    )

@login_required
@user_passes_test(is_staff_user)
def staff_import_data(request):

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return render(request, 'assistant/staff_import_data.html', {
                'error': 'Please select an Excel file.'
            })

        if not uploaded_file.name.lower().endswith('.xlsx'):
            return render(request, 'assistant/staff_import_data.html', {
                'error': 'Only .xlsx Excel files are supported.'
            })

        try:
            sheets = pd.read_excel(uploaded_file, sheet_name=None)

            imported = {
                'notices': 0,
                'assignments': 0,
                'timetable': 0,
                'faq': 0,
            }

            # ---------------- NOTICES ----------------
            if 'Notices' in sheets:
                df = sheets['Notices'].fillna('')

                for _, row in df.iterrows():
                    title = str(row.get('title', '')).strip()
                    description = str(row.get('description', '')).strip()

                    if title and description:
                        obj, created = Notice.objects.get_or_create(
                            title=title,
                            description=description
                        )

                        if created:
                            imported['notices'] += 1

            # ---------------- ASSIGNMENTS ----------------
            if 'Assignments' in sheets:
                df = sheets['Assignments'].fillna('')

                for _, row in df.iterrows():
                    title = str(row.get('title', '')).strip()
                    subject = str(row.get('subject', '')).strip()
                    description = str(row.get('description', '')).strip()
                    due_date = str(row.get('due_date', '')).strip()

                    if title and subject and due_date:
                        try:
                            parsed_date = pd.to_datetime(
                                due_date
                            ).date()

                            obj, created = Assignment.objects.get_or_create(
                                title=title,
                                subject=subject,
                                due_date=parsed_date,
                                defaults={
                                    'description': description
                                }
                            )

                            if created:
                                imported['assignments'] += 1

                        except Exception:
                            continue

            # ---------------- TIMETABLE ----------------
            if 'Timetable' in sheets:
                df = sheets['Timetable'].fillna('')

                for _, row in df.iterrows():
                    timetable_type = str(
                        row.get('timetable_type', 'student')
                    ).strip().lower()

                    day = str(row.get('day', '')).strip()
                    subject = str(row.get('subject', '')).strip()
                    start_time = str(row.get('start_time', '')).strip()
                    end_time = str(row.get('end_time', '')).strip()

                    if not timetable_type:
                        timetable_type = 'student'

                    if (
                        timetable_type in ['student', 'staff']
                        and day
                        and subject
                        and start_time
                        and end_time
                    ):
                        try:
                            parsed_start = pd.to_datetime(
                                start_time
                            ).time()

                            parsed_end = pd.to_datetime(
                                end_time
                            ).time()

                            obj, created = Timetable.objects.get_or_create(
                                timetable_type=timetable_type,
                                day=day,
                                subject=subject,
                                start_time=parsed_start,
                                end_time=parsed_end
                            )

                            if created:
                                imported['timetable'] += 1

                        except Exception:
                            continue

            # ---------------- FAQ ----------------
            if 'FAQ' in sheets:
                df = sheets['FAQ'].fillna('')

                for _, row in df.iterrows():
                    question = str(row.get('question', '')).strip()
                    answer = str(row.get('answer', '')).strip()

                    if question and answer:
                        obj, created = FAQ.objects.get_or_create(
                            question=question,
                            defaults={
                                'answer': answer
                            }
                        )

                        if created:
                            imported['faq'] += 1

            return render(
                request,
                'assistant/staff_import_data.html',
                {
                    'success': True,
                    'imported': imported
                }
            )

        except Exception as e:
            return render(
                request,
                'assistant/staff_import_data.html',
                {
                    'error': f'Import failed: {str(e)}'
                }
            )

    return render(
        request,
        'assistant/staff_import_data.html'
    )