from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.model_training.evaluate_multilabel import evaluate_multilabel

# Create your views here.

@api_view(["POST"])
def check_elements(request):
    elements = [elem["text"] for elem in request.data["elements"]]
    try:
        result = evaluate_multilabel(elements)
        return Response(result, status=status.HTTP_200_OK)
    except:
        print(elements)
        return Response("", status=status.HTTP_400_BAD_REQUEST)

