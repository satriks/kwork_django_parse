from django.shortcuts import render

# Create your views here.
# myapp/views.py
from django.shortcuts import render
from .models import Offers
from .tasks import my_background_task
from django.http import JsonResponse

# def start_task(request):
#     job = my_background_task.delay(5)  # Запускаем задачу на 5 секунд
#     return render(request, 'myapp/task_started.html', {'job_id': job.id})



def offers_list(request):
    status_filter = request.GET.get('status', None)
    if status_filter:
        offers = Offers.objects.filter(status=status_filter)
    else:
        offers = Offers.objects.all()

    return render(request, 'offers/offers_list.html', {'offers': offers})


def change_status(request, offer_id, new_status):
    try:
        offer = Offers.objects.get(id=offer_id)
        offer.status = new_status
        offer.save()
        return JsonResponse({'status': 'success'})
    except Offers.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)