from rest_framework import generics
from .models import Property
from .serializers import PropertySerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.views import APIView

class TestView(APIView):
    def get(self, request):
        return JsonResponse({"message": "It works!"})


from rest_framework import generics, filters

class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'location']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Получить, обновить или удалить конкретное объявление
class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PropertyForm

@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.user = request.user  
            property_obj.save()
            return redirect('property_list')  
    else:
        form = PropertyForm()

    return render(request, 'listings/add_property.html', {'form': form})
