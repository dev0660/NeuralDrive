from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from AAIApp.forms import InputSignIn, LogSignUpForm
from .models import CallRecord, CustomUser, Dealership, CallAnalysis

from vapi import Vapi
from openai import OpenAI

import os
import re
import json


def home(request):
    return render(request, "demoHomePage.html")


def feature(request):
    return render(request, "demoFeaturePage.html")


def faq(request):
    return render(request, "demoFAQPage.html")


def testimonials(request):
    return render(request, "demoTestimonialsPage.html")


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
        print("Form errors:", form.errors)
    else:
        form = LogSignUpForm()

    return render(request, "signup.html", {"form": form})


def form_signin(request):
    if request.method == "POST":
        form = InputSignIn(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("successful_login")
            messages.error(request, "Invalid username or password")
    else:
        form = InputSignIn()

    return render(request, "signin.html", {"form": form})


def successful_login(request):
    return render(
        request,
        "successful_login.html",
        {"message": "Congratulations, you successfully created an account!"},
    )


def customer_discovery(request):
    return render(request, "customer_discovery.html")


def inbound_calls(request):
    return render(request, "inbound_calls.html")


@login_required(login_url="/signin/")
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
        "46", "47", "48", "49", "50",
    ]

    buttons = []
    for i, name in enumerate(names, start=1):
        record = (
            CallAnalysis.objects
            .filter(user=request.user, assistant_name=name, outcome="pass", success_score__isnull=False)
            .order_by("-success_score")
            .first()
        )

        if record:
            score = record.success_score
            if score == 100:
                color = "bg-amber-500"
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

    return render(request, "outbound_calls.html", {"buttons": buttons})


def normalize_phone_number(phone_number):
    digits = re.sub(r"\D", "", phone_number or "")
    if digits and not digits.startswith("1"):
        digits = "1" + digits
    return f"+{digits}" if digits else ""


def is_admin(user):
    return getattr(user, "is_admin_user", False)


@login_required(login_url="/signin/")
@user_passes_test(is_admin, login_url="/signin/")
def admin_dashboard(request):
    User = get_user_model()
    selected_user_id = request.GET.get("user")

    if selected_user_id:
        call_data = (
            CallRecord.objects
            .select_related("user")
            .filter(user_id=selected_user_id)
            .order_by("-timestamp")
        )
    else:
        call_data = (
            CallRecord.objects
            .select_related("user")
            .order_by("-timestamp")
        )

    users = User.objects.all().order_by("username")

    return render(request, "admin_dashboard.html", {
        "call_data": call_data,
        "users": users,
        "selected_user_id": selected_user_id,
    })


def dealership_leaderboard(request):
    leaderboard = (
        Dealership.objects.annotate(
            total_calls=Count("users__callrecord"),
            total_duration=Sum("users__callrecord__duration"),
            average_score=Avg("users__callrecord__success_score"),
        ).order_by("-average_score")
    )

    return render(request, "dealership_leaderboard.html", {"leaderboard": leaderboard})


@login_required(login_url="/signin/")
def call_history_fred_davis(request, assistant_name):
    call_records = (
        CallAnalysis.objects
        .filter(user=request.user, assistant_name=assistant_name)
        .order_by("-timestamp")
    )

    return render(request, "call_history_fred_davis.html", {
        "assistant_name": assistant_name,
        "call_records": call_records,
    })


@login_required(login_url="/signin/")
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


def build_call_analysis_context(call):
    transcript = call.transcript or "No transcript available"

    formatted_transcript = []
    for line in transcript.split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            speaker, message = line.split(":", 1)
            formatted_transcript.append({
                "speaker": speaker.strip(),
                "message": message.strip(),
            })
        else:
            formatted_transcript.append({
                "speaker": "Unknown",
                "message": line,
            })

    sections = [
        {"label": "(20%) Acknowledging Objections Respectfully", "data": {
            "score": call.acknowledging_score,
            "reason": call.acknowledging_reason,
            "suggestion": call.acknowledging_suggestion,
        }},
        {"label": "(20%) Reframing with Empathy, Value, or Curiosity", "data": {
            "score": call.reframing_score,
            "reason": call.reframing_reason,
            "suggestion": call.reframing_suggestion,
        }},
        {"label": "(20%) Handling Resistance Calmly", "data": {
            "score": call.handling_score,
            "reason": call.handling_reason,
            "suggestion": call.handling_suggestion,
        }},
        {"label": "(20%) Securing Soft Commitment or Follow-Up", "data": {
            "score": call.securing_score,
            "reason": call.securing_reason,
            "suggestion": call.securing_suggestion,
        }},
        {"label": "(20%) Leaving the Customer Feeling Respected", "data": {
            "score": call.respect_score,
            "reason": call.respect_reason,
            "suggestion": call.respect_suggestion,
        }},
    ]

    return {
        "transcript": transcript,
        "formatted_transcript": formatted_transcript,
        "recording_url": call.recording_url,
        "summary": None,
        "structured_data": {"outcome": call.outcome} if call.outcome else {},
        "structured_data_multi": [],
        "success_evaluation": call.success_score,
        "sections": sections,
        "total_score": call.success_score if call.success_score is not None else "N/A",
        "final_comments": call.final_comments or "N/A",
        "outcome": call.outcome,
        "duration": call.duration or 0,
        "empty_state_message": None,
    }


def build_empty_state_context(assistant_name):
    return {
        "transcript": "No transcript available",
        "formatted_transcript": [],
        "recording_url": None,
        "summary": None,
        "structured_data": {},
        "structured_data_multi": [],
        "success_evaluation": None,
        "sections": [],
        "total_score": "N/A",
        "final_comments": "N/A",
        "outcome": None,
        "duration": 0,
        "empty_state_message": f"You must make a call with {assistant_name} before results can be shown here.",
    }


def is_call_fully_evaluated(call):
    return bool(
        call
        and call.success_score is not None
        and call.acknowledging_score is not None
        and call.reframing_score is not None
        and call.handling_score is not None
        and call.securing_score is not None
        and call.respect_score is not None
        and call.transcript
        and call.transcript.strip()
    )


def parse_transcript(transcript):
    formatted_transcript = []
    if transcript:
        for line in transcript.split("\n"):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                speaker, message = line.split(":", 1)
                formatted_transcript.append({
                    "speaker": speaker.strip(),
                    "message": message.strip(),
                })
            else:
                formatted_transcript.append({
                    "speaker": "Unknown",
                    "message": line,
                })
    return formatted_transcript


def compute_duration_from_artifact(artifact):
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

    return int(round(max_seconds))


def handle_personality_test(request, assistant_id, assistant_name, template_name):
    force_refresh = request.GET.get("refresh") == "1"

    # Normal page load: DB only
    existing_cached_call = (
        CallAnalysis.objects
        .filter(user=request.user, assistant_name=assistant_name)
        .order_by("-timestamp")
        .first()
    )

    if not force_refresh:
        if is_call_fully_evaluated(existing_cached_call):
            print(f"⚡ Loading cached analysis from DB for {assistant_name}")
            return render(request, template_name, build_call_analysis_context(existing_cached_call))

        print(f"ℹ️ No cached call found for {assistant_name}. Not calling Vapi.")
        return render(request, template_name, build_empty_state_context(assistant_name))

    print(f"🔄 Manual refresh requested for {assistant_name}")

    try:
        vapi_client = Vapi(token=os.getenv("VAPI_TOKEN"))
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        calls = vapi_client.calls.list(
            assistant_id=assistant_id,
            limit=50,
        )
        print("📞 Total calls returned:", len(calls))

        customer_number = normalize_phone_number(getattr(request.user, "phone_number", ""))

        matching_call = next(
            (
                call for call in calls
                if getattr(call, "customer", None)
                and getattr(call.customer, "number", None)
                and customer_number
                and customer_number[-7:] in call.customer.number[-7:]
            ),
            None,
        )

        if not matching_call:
            context = build_empty_state_context(assistant_name)
            context["empty_state_message"] = (
                f"No matching Vapi call was found yet for {assistant_name}. "
                f"Make a call, then press Refresh Latest Call."
            )
            return render(request, template_name, context)

        detailed_call = vapi_client.calls.get(matching_call.id)
        artifact = getattr(detailed_call, "artifact", None)
        call_id = getattr(detailed_call, "id", None)
        transcript = getattr(artifact, "transcript", None) or "No transcript available"
        recording_url = getattr(artifact, "recording_url", None)

        raw_analysis = getattr(detailed_call, "analysis", None)
        if raw_analysis is None:
            analysis = {}
        elif isinstance(raw_analysis, dict):
            analysis = raw_analysis
        else:
            analysis = raw_analysis.__dict__

        print("📊 Converted analysis object:", json.dumps(analysis, indent=2))

        summary = analysis.get("summary")
        structured_data = analysis.get("structuredData") or analysis.get("structured_data") or {}
        structured_data_multi = analysis.get("structuredDataMulti") or analysis.get("structured_data_multi") or []
        success_evaluation = analysis.get("successEvaluation") or analysis.get("success_evaluation")

        outcome = structured_data.get("outcome")
        if not outcome and structured_data_multi:
            outcome = structured_data_multi[0].get("outcome")

        print("✅ Extracted outcome:", outcome)

        duration = compute_duration_from_artifact(artifact)
        print(f"⏱️ Computed call duration: {duration} seconds (~{duration / 60:.2f} minutes)")

        existing_call = CallAnalysis.objects.filter(user=request.user, call_id=call_id).first()

        if (
            is_call_fully_evaluated(existing_call)
            and (existing_call.transcript or "").strip() == transcript.strip()
        ):
            print("📂 Exact call already fully evaluated — skipping GPT.")
            return redirect(request.path)

        print("🧠 Running GPT evaluation...")

        messages_for_gpt = [
            {
                "role": "developer",
                "content": (
                    "You are an expert automotive sales call evaluator. "
                    "Your job is to evaluate calls using a strict rubric and return JSON only."
                ),
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
- Must be valid JSON only.
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
""",
            },
        ]

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

        defaults = {
            "timestamp": timezone.now(),
            "assistant_name": assistant_name,
            "outcome": outcome,
            "recording_url": recording_url,
            "transcript": transcript,
            "duration": duration,
            "success_score": evaluation_data.get("total_score"),
            "final_comments": evaluation_data.get("final_comments"),
            "acknowledging_score": evaluation_data.get("acknowledging", {}).get("score"),
            "acknowledging_reason": evaluation_data.get("acknowledging", {}).get("reason"),
            "acknowledging_suggestion": evaluation_data.get("acknowledging", {}).get("suggestion"),
            "reframing_score": evaluation_data.get("reframing", {}).get("score"),
            "reframing_reason": evaluation_data.get("reframing", {}).get("reason"),
            "reframing_suggestion": evaluation_data.get("reframing", {}).get("suggestion"),
            "handling_score": evaluation_data.get("handling", {}).get("score"),
            "handling_reason": evaluation_data.get("handling", {}).get("reason"),
            "handling_suggestion": evaluation_data.get("handling", {}).get("suggestion"),
            "securing_score": evaluation_data.get("securing", {}).get("score"),
            "securing_reason": evaluation_data.get("securing", {}).get("reason"),
            "securing_suggestion": evaluation_data.get("securing", {}).get("suggestion"),
            "respect_score": evaluation_data.get("respect", {}).get("score"),
            "respect_reason": evaluation_data.get("respect", {}).get("reason"),
            "respect_suggestion": evaluation_data.get("respect", {}).get("suggestion"),
        }

        obj, created = CallAnalysis.objects.update_or_create(
            user=request.user,
            call_id=call_id,
            defaults=defaults,
        )

        if created:
            print("💾 Created new call analysis record.")
        else:
            print("✏️ Updated existing call analysis record.")

        return redirect(request.path)

    except Exception as e:
        print("❌ Error:", e)
        context = build_empty_state_context(assistant_name)
        context["empty_state_message"] = (
            f"We couldn’t refresh the latest call for {assistant_name} right now. "
            f"Please try again."
        )
        return render(request, template_name, context)


@login_required(login_url="/signin/")
def fred_davis(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("FRED_DAVIS_ASSISTANT_ID"),
        assistant_name="Fred Davis",
        template_name="fred_davis.html",
    )


@login_required(login_url="/signin/")
def jordan_reyes(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("JORDAN_REYES_ASSISTANT_ID"),
        assistant_name="Jordan Reyes",
        template_name="jordan_reyes.html",
    )


@login_required(login_url="/signin/")
def alex_martinez(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("ALEX_MARTINEZ_ASSISTANT_ID"),
        assistant_name="Alex Martinez",
        template_name="alex_martinez.html",
    )


@login_required(login_url="/signin/")
def priya_shah(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("PRIYA_SHAH_ASSISTANT_ID"),
        assistant_name="Priya Shah",
        template_name="priya_shah.html",
    )


@login_required(login_url="/signin/")
def chase_montgomery_III(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("CHASE_MONTGOMERY_ASSISTANT_ID"),
        assistant_name="Chase Montgomery III",
        template_name="chase_montgomery_III.html",
    )


@login_required(login_url="/signin/")
def sofia_delgado(request):
    return handle_personality_test(
        request,
        assistant_id=os.getenv("SOFIA_DELGADO_ASSISTANT_ID"),
        assistant_name="Sofia Delgado",
        template_name="sofia_delgado.html",
    )