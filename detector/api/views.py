from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.model_training.evaluate_tiny_multilabel import evaluate_multilabel
from django.shortcuts import get_object_or_404
from .forms import demoForm
# from .models import Article
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

def home(request):
    return render(request, "api/home.html")

def about(request):
    return render(request, "api/about.html")

def article_view(request):
    # article = get_object_or_404(Article, pk=pk)
    # context = {
    #     "title": article.title,
    #     "text": article.text,
    # }
    return render(request, "api/article_view.html")

# def articles_list(request):
#     return render(request, "api/article_home.html")
def demo_view(request):
    form = demoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            text = form.cleaned_data.get("text")
            result = evaluate_multilabel([text])
            result = result["elements"][0]["dark_patterns"]
            max_type="No Dark Pattern Detected"
            max_result = 0.5
            for x in result:
                if x["probability"]>0.5:
                    max_result=x["probability"]
                    max_type = x["type"]
            # print(result["elements"][0]["dark_patterns"])
            return render(request, "api/demo.html", {"form":form, "response": max_type})
    return render(request, "api/demo.html", {"form":form, "response":""})