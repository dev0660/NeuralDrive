from django.shortcuts import render, redirect
from AAIApp.forms import InputSignIn, LogSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from vapi import Vapi
import requests, re, json
from django.contrib.auth.decorators import user_passes_test
from .models import CallRecord, CustomUser, Dealership, CallAnalysis
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
import datetime
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Sum, Avg
from openai import OpenAI
import os
import json
from django.utils import timezone


def home(request): 
    return render(request, 'demoHomePage.html')

def feature(request):
    return render(request, 'demoFeaturePage.html')

def faq(request):
    return render(request, 'demoFAQPage.html')

def testimonials(request):
    return render(request, 'demoTestimonialsPage.html')

def form_signup(request):
    if request.method == "POST":
        form = LogSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Congratulations, you successfully created an account! Please sign in."
            )
            return redirect("signin")
        else:
            print("Form errors:", form.errors)  # For debugging
    else:
        form = LogSignUpForm()

    return render(request, "signup.html", {"form": form})

def form_signin(request):
    if request.method == "POST":
        form = InputSignIn(request.POST)  # ✅ create form with POST data
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("successful_login")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = InputSignIn()  # ✅ empty form for GET requests

    # ✅ Always render with the same `request` context
    return render(request, "signin.html", {"form": form})

def successful_login(request):
    context = {"message": "Congratulations, you successfully created an account!"}
    return render(request, "successful_login.html", context)

def customer_discovery(request):
    return render(request, 'customer_discovery.html')

def outbound_calls(request):
    return render(request, 'outbound_calls.html')

def inbound_calls(request):
    return render(request, 'inbound_calls.html')

def outbound_calls(request):
    names = [
        "Fred Davis", "Jordan Reyes", "Alex Martinez", "Priya Shah", "Chase Montgomery III",
        "Sofia Delgado", "7", "8", "9", "10",
        "11", "12", "13", "14", "15",
        "16", "17", "18", "19", "20",
        "21", "22", "23", "24", "25",
        "26", "27", "28", "29", "30",
        "31", "32", "33", "34", "35",
        "36", "37", "38", "39", "40",
        "41", "42", "43", "44", "45",
        "46", "47", "48", "49", "50"
    ]

    buttons = []
    for i, name in enumerate(names, start=1):
        record = (
            CallAnalysis.objects
            .filter(user=request.user, assistant_name=name, outcome="pass", success_score__isnull=False)
            .order_by("-success_score")
            .first()
        )

        # Score-based color logic
        if record:
            score = record.success_score
            if score == 100:
                color = "bg-amber-500" # or "bg-yellow-200" for a rich gold tone
            elif score >= 90:
                color = "bg-green-600"
            elif score >= 75:
                color = "bg-lime-500"
            elif score >= 60:
                color = "bg-yellow-400"
            elif score >= 45:
                color = "bg-orange-400"
            elif score >= 30:
                color = "bg-orange-500"
            elif score >= 15:
                color = "bg-red-500"
            else:
                color = "bg-red-600"
        else:
            color = "bg-blue-500"

        buttons.append({
            "name": name,
            "href": f"/outbound_call_{i}/",
            "color": color,
        })

    return render(request, 'outbound_calls.html', {"buttons": buttons})

def normalize_phone_number(phone_number):
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    # Add country code if needed
    if not digits.startswith('1'):
        digits = '1' + digits
    return f'+{digits}'

# ✅ Admin permission check
def is_admin(user):
    return getattr(user, 'is_admin_user', False)

# 🛠️ Admin Dashboard - View all calls by users
@login_required(login_url='/signin/')
@user_passes_test(is_admin, login_url='/signin/')
def admin_dashboard(request):
    User = get_user_model()
    selected_user_id = request.GET.get('user')

    if selected_user_id:
        call_data = (
            CallRecord.objects
            .select_related('user')
            .filter(user_id=selected_user_id)
            .order_by('-timestamp')
        )
    else:
        call_data = (
            CallRecord.objects
            .select_related('user')
            .order_by('-timestamp')
        )

    users = User.objects.all().order_by('username')

    return render(request, 'admin_dashboard.html', {
        "call_data": call_data,
        "users": users,
        "selected_user_id": selected_user_id,
    })


# 🏆 Dealership Leaderboard - Aggregated stats
def dealership_leaderboard(request):
    leaderboard = (
        Dealership.objects.annotate(
            total_calls=Count('users__callrecord'),
            total_duration=Sum('users__callrecord__duration'),
            average_score=Avg('users__callrecord__success_score')
        ).order_by('-average_score')
    )

    return render(request, 'dealership_leaderboard.html', {'leaderboard': leaderboard})


# 📜 Call History - For a specific personality
@login_required(login_url='/signin/')
def call_history_fred_davis(request, assistant_name):
    call_records = (
        CallAnalysis.objects
        .filter(user=request.user, assistant_name=assistant_name)
        .order_by('-timestamp')
    )

    return render(request, 'call_history_fred_davis.html', {
        'assistant_name': assistant_name,
        'call_records': call_records,
    })


# 📡 API endpoint - Get call record as JSON
@login_required(login_url='/signin/')
def call_record_api(request, call_id):
    try:
        record = CallRecord.objects.get(call_id=call_id, user=request.user)
        return JsonResponse({
            "timestamp": record.timestamp.strftime("%B %d, %Y %I:%M %p"),
            "duration": record.duration,
            "outcome": record.outcome,
            "success_score": record.success_score,
            "success_evaluation": record.success_evaluation,
            "transcript": record.transcript,
        })
    except CallRecord.DoesNotExist:
        return JsonResponse({"error": "Call not found"}, status=404)

def handle_personality_test(request, assistant_id, assistant_name, template_name):
    vapi_client = Vapi(token=os.getenv("VAPI_TOKEN"))
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # ✅ Default values
    transcript = "No transcript available"
    formatted_transcript = []
    recording_url = None
    duration = 0
    outcome = None
    total_score = "N/A"
    final_comments = "N/A"
    sections = []
    evaluation_data = {}

    # ✅ Analysis defaults
    summary = None
    structured_data = {}
    structured_data_multi = []
    success_evaluation = None

    try:
        # 1️⃣ Fetch recent calls
        calls = vapi_client.calls.list(
            assistant_id=assistant_id,
            limit=50,
        )
        print("📞 Total calls returned:", len(calls))

        # 2️⃣ Match call by user's phone number
        customer_number = normalize_phone_number(request.user.phone_number)
        matching_call = next(
            (call for call in calls if call.customer and customer_number[-7:] in call.customer.number[-7:]),
            calls[0] if calls else None
        )

        if not matching_call:
            return render(request, template_name, {
                "summary": "No matching call found",
                "transcript": transcript,
                "sections": sections,
                "total_score": total_score,
                "final_comments": final_comments
            })

        # 3️⃣ Retrieve detailed call info
        detailed_call = vapi_client.calls.get(matching_call.id)
        artifact = getattr(detailed_call, "artifact", None)
        call_id = getattr(detailed_call, "id", None)
        transcript = getattr(artifact, "transcript", None) or "No transcript available"
        recording_url = getattr(artifact, "recording_url", None)

        # 🧠 Extract and convert analysis to dict
        raw_analysis = getattr(detailed_call, "analysis", None)
        if raw_analysis is None:
            analysis = {}
        elif isinstance(raw_analysis, dict):
            analysis = raw_analysis
        else:
            analysis = raw_analysis.__dict__

        print("📊 Converted analysis object:", json.dumps(analysis, indent=2))

        # ✅ Extract analysis fields
        summary = analysis.get("summary")
        structured_data = (
            analysis.get("structuredData")
            or analysis.get("structured_data")
            or {}
        )
        structured_data_multi = (
            analysis.get("structuredDataMulti")
            or analysis.get("structured_data_multi")
            or []
        )
        success_evaluation = (
            analysis.get("successEvaluation")
            or analysis.get("success_evaluation")
        )

        # ✅ Extract outcome
        outcome = structured_data.get("outcome")
        if not outcome and structured_data_multi:
            outcome = structured_data_multi[0].get("outcome")
        print("✅ Extracted outcome:", outcome)

        # ✅ Compute call duration
        messages = []
        if isinstance(artifact, dict):
            messages = artifact.get("messages", [])
        elif hasattr(artifact, "__dict__"):
            messages = getattr(artifact, "messages", [])
        elif isinstance(artifact, str):
            try:
                artifact_json = json.loads(artifact)
                messages = artifact_json.get("messages", [])
            except json.JSONDecodeError:
                messages = []

        max_seconds = 0.0
        for msg in messages:
            if not isinstance(msg, dict):
                msg = msg.__dict__ if hasattr(msg, "__dict__") else {}
            secs = msg.get("secondsFromStart") or msg.get("seconds_from_start")
            if secs is None and isinstance(msg.get("result"), dict):
                secs = msg["result"].get("secondsFromStart") or msg["result"].get("seconds_from_start")
            if secs is None and isinstance(msg.get("message"), dict):
                secs = msg["message"].get("secondsFromStart") or msg["message"].get("seconds_from_start")
            try:
                if secs is not None:
                    max_seconds = max(max_seconds, float(secs))
            except (ValueError, TypeError):
                continue

        duration = int(round(max_seconds))
        print(f"⏱️ Computed call duration: {duration} seconds (~{duration/60:.2f} minutes)")

        # ✅ Format transcript
        formatted_transcript = []
        if transcript:
            for line in transcript.split("\n"):
                if ":" in line:
                    speaker, message = line.split(":", 1)
                    formatted_transcript.append({
                        "speaker": speaker.strip(),
                        "message": message.strip()
                    })
                else:
                    formatted_transcript.append({
                        "speaker": "Unknown",
                        "message": line.strip()
                    })

        # ✅ Check existing evaluation
        existing_call = CallAnalysis.objects.filter(user=request.user, call_id=call_id).first()

        # ✅ Re-run GPT if transcript changed or evaluation is missing
        call_fully_evaluated = (
            existing_call
            and existing_call.success_score not in [None, "", "N/A"]
            and existing_call.acknowledging_score not in [None, "", "N/A"]
            and existing_call.reframing_score not in [None, "", "N/A"]
            and existing_call.handling_score not in [None, "", "N/A"]
            and existing_call.securing_score not in [None, "", "N/A"]
            and existing_call.respect_score not in [None, "", "N/A"]
            and existing_call.transcript.strip() == transcript.strip()
        )

        if call_fully_evaluated:
            print("📂 Call already fully evaluated — skipping GPT.")
            total_score = existing_call.success_score or "N/A"
            final_comments = existing_call.final_comments or "N/A"
            outcome = existing_call.outcome or outcome
            recording_url = existing_call.recording_url or recording_url
            duration = existing_call.duration or duration
            sections = [
                {"label": "(20%) Acknowledging Objections Respectfully", "data": {
                    "score": existing_call.acknowledging_score,
                    "reason": existing_call.acknowledging_reason,
                    "suggestion": existing_call.acknowledging_suggestion,
                }},
                {"label": "(20%) Reframing with Empathy, Value, or Curiosity", "data": {
                    "score": existing_call.reframing_score,
                    "reason": existing_call.reframing_reason,
                    "suggestion": existing_call.reframing_suggestion,
                }},
                {"label": "(20%) Handling Resistance Calmly", "data": {
                    "score": existing_call.handling_score,
                    "reason": existing_call.handling_reason,
                    "suggestion": existing_call.handling_suggestion,
                }},
                {"label": "(20%) Securing Soft Commitment or Follow-Up", "data": {
                    "score": existing_call.securing_score,
                    "reason": existing_call.securing_reason,
                    "suggestion": existing_call.securing_suggestion,
                }},
                {"label": "(20%) Leaving the Customer Feeling Respected", "data": {
                    "score": existing_call.respect_score,
                    "reason": existing_call.respect_reason,
                    "suggestion": existing_call.respect_suggestion,
                }},
            ]

        else:
            print("🧠 Running GPT evaluation...")
            messages_for_gpt = [
                {
                    "role": "developer",
                    "content": (
                        "You are an expert automotive sales call evaluator. "
                        "Your job is to evaluate calls using a strict rubric and return JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Using the transcript below, evaluate the salesperson's performance using this rubric:

(20%) Acknowledging Objections Respectfully  
(20%) Reframing with Empathy, Value, or Curiosity  
(20%) Handling Resistance Calmly  
(20%) Securing Soft Commitment or Follow-Up  
(20%) Leaving the Customer Feeling Respected  

✅ Total Score: __ / 100  
💡 Final Comments: __

⚠️ OUTPUT REQUIREMENTS:
- Must be **valid JSON only**.
- Follow this schema exactly:
{{
  "acknowledging": {{"score": "", "reason": "", "suggestion": ""}},
  "reframing": {{"score": "", "reason": "", "suggestion": ""}},
  "handling": {{"score": "", "reason": "", "suggestion": ""}},
  "securing": {{"score": "", "reason": "", "suggestion": ""}},
  "respect": {{"score": "", "reason": "", "suggestion": ""}},
  "total_score": "",
  "final_comments": ""
}}

Transcript:
{transcript}
"""
                }
            ]

            # 🧠 GPT Evaluation
            openai_response = openai_client.responses.create(
                model="gpt-5",
                input=messages_for_gpt,
            )
            raw_text = getattr(openai_response, "output_text", "{}")
            json_match = re.search(r"\{[\s\S]*\}", raw_text)
            json_string = json_match.group(0) if json_match else "{}"

            try:
                evaluation_data = json.loads(json_string)
            except json.JSONDecodeError:
                evaluation_data = {}

            # ✅ Save or update the call analysis
            if existing_call:
                print("✏️ Updating existing call analysis...")
                existing_call.outcome = outcome
                existing_call.recording_url = recording_url
                existing_call.transcript = transcript
                existing_call.duration = duration
                existing_call.success_score = evaluation_data.get("total_score")
                existing_call.final_comments = evaluation_data.get("final_comments")
                existing_call.acknowledging_score = evaluation_data.get("acknowledging", {}).get("score")
                existing_call.acknowledging_reason = evaluation_data.get("acknowledging", {}).get("reason")
                existing_call.acknowledging_suggestion = evaluation_data.get("acknowledging", {}).get("suggestion")
                existing_call.reframing_score = evaluation_data.get("reframing", {}).get("score")
                existing_call.reframing_reason = evaluation_data.get("reframing", {}).get("reason")
                existing_call.reframing_suggestion = evaluation_data.get("reframing", {}).get("suggestion")
                existing_call.handling_score = evaluation_data.get("handling", {}).get("score")
                existing_call.handling_reason = evaluation_data.get("handling", {}).get("reason")
                existing_call.handling_suggestion = evaluation_data.get("handling", {}).get("suggestion")
                existing_call.securing_score = evaluation_data.get("securing", {}).get("score")
                existing_call.securing_reason = evaluation_data.get("securing", {}).get("reason")
                existing_call.securing_suggestion = evaluation_data.get("securing", {}).get("suggestion")
                existing_call.respect_score = evaluation_data.get("respect", {}).get("score")
                existing_call.respect_reason = evaluation_data.get("respect", {}).get("reason")
                existing_call.respect_suggestion = evaluation_data.get("respect", {}).get("suggestion")
                existing_call.save()
            else:
                print("💾 Creating new call analysis record...")
                CallAnalysis.objects.create(
                    user=request.user,
                    timestamp=timezone.now(),
                    call_id=call_id,
                    assistant_name=assistant_name,
                    outcome=outcome,
                    recording_url=recording_url,
                    transcript=transcript,
                    duration=duration,
                    success_score=evaluation_data.get("total_score"),
                    final_comments=evaluation_data.get("final_comments"),
                    acknowledging_score=evaluation_data.get("acknowledging", {}).get("score"),
                    acknowledging_reason=evaluation_data.get("acknowledging", {}).get("reason"),
                    acknowledging_suggestion=evaluation_data.get("acknowledging", {}).get("suggestion"),
                    reframing_score=evaluation_data.get("reframing", {}).get("score"),
                    reframing_reason=evaluation_data.get("reframing", {}).get("reason"),
                    reframing_suggestion=evaluation_data.get("reframing", {}).get("suggestion"),
                    handling_score=evaluation_data.get("handling", {}).get("score"),
                    handling_reason=evaluation_data.get("handling", {}).get("reason"),
                    handling_suggestion=evaluation_data.get("handling", {}).get("suggestion"),
                    securing_score=evaluation_data.get("securing", {}).get("score"),
                    securing_reason=evaluation_data.get("securing", {}).get("reason"),
                    securing_suggestion=evaluation_data.get("securing", {}).get("suggestion"),
                    respect_score=evaluation_data.get("respect", {}).get("score"),
                    respect_reason=evaluation_data.get("respect", {}).get("reason"),
                    respect_suggestion=evaluation_data.get("respect", {}).get("suggestion"),
                )

    except Exception as e:
        print("❌ Error:", e)

    # ✅ Render final context
    return render(request, template_name, {
        "transcript": transcript,
        "formatted_transcript": formatted_transcript,
        "recording_url": recording_url,
        "summary": summary,
        "structured_data": structured_data,
        "structured_data_multi": structured_data_multi,
        "success_evaluation": success_evaluation,
        "sections": sections,
        "total_score": total_score,
        "final_comments": final_comments,
        "outcome": outcome,
        "duration": duration,
    })

def fred_davis(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("FRED_DAVIS_ASSISTANT_ID"),
        assistant_name="Fred Davis",
        template_name="fred_davis.html"
    )

def jordan_reyes(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("JORDAN_REYES_ASSISTANT_ID"),
        assistant_name="Jordan Reyes",
        template_name="jordan_reyes.html"
    )

def alex_martinez(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("ALEX_MARTINEZ_ASSISTANT_ID"),
        assistant_name="Alex Martinez",
        template_name="alex_martinez.html"
    )
    
def priya_shah(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("PRIYA_SHAH_ASSISTANT_ID"),
        assistant_name="Priya Shah",
        template_name="priya_shah.html"
    )
    
def chase_montgomery_III(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("CHASE_MONTGOMERY_ASSISTANT_ID"),
        assistant_name="Chase Montgomery III",
        template_name="chase_montgomery_III.html"
    )  

def sofia_delgado(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("SOFIA_DELGADO_ASSISTANT_ID"),
        assistant_name="Sofia Delgado",
        template_name="sofia_delgado.html"
    )
    
