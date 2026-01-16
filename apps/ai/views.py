import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.ai.hf_client import hf_chat
from apps.ai.reports import get_inactive_clients
from apps.ai.prompts import build_inactive_clients_prompt


class InactiveClientsHelperView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        window_days = int(request.data.get('window_days', 30))
        studio_name = request.data.get('studio_name', "Reforme Pilates")

        rows = get_inactive_clients(window_days=window_days, limit=200)
        system_prompt, user_prompt = build_inactive_clients_prompt(
            studio_name=studio_name, window_days=window_days, rows=rows)

        raw = hf_chat(system_prompt, user_prompt)

        try:
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start:end+1])
        except Exception:
            return Response({"error": "AI did not return valid JSON", "raw": raw}, status=500)

        return Response({
            "window_days": window_days,
            "inactive_clients": rows,
            "ai": parsed,
        })
