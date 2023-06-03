from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from OMDApp.models import Turno, Veterinario, Perro
from OMDApp.decorators import email_verification_required
from OMDApp.forms.turns_form import (AskForTurnForm, AttendTurnForm)
from django.views.decorators.cache import cache_control
from django.db.models import Q
from datetime import date
import json
from OMDApp.views.helpers import (turn_type_mapping, turn_hour_mapping, actual_turn_hour_check,
                                    generate_date, append_data)


# Create your views here

from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def AskForTurn(request):
    if request.method == "POST":
        form = AskForTurnForm(request.POST)
        if form.is_valid():
            turn = form.save(commit=False)

            if turn.solicited_by.castrated:
                messages.error(request, "No puede solicitar un turno de castración para un perro castrado")
                return redirect(reverse("askForTurn"))

            same_date_turns = list(Turno.objects.filter(date=turn.date, hour=turn.hour))
            if len(same_date_turns) == 20:
                hours = str(turn_hour_mapping().get(turn.hour)).split(': ')[1]
                message = 'No quedan turnos disponibles el %s de %s' % (turn.date.strftime('%d/%m/%Y'), hours)
                messages.error(request, message)
                return redirect(reverse("askForTurn"))

            turn.save()
            messages.success(request, f'Solicitud de turno exitosa')
            return redirect(reverse("home"))
    user_dogs = Perro.objects.filter(owner=request.user)
    form = AskForTurnForm(user_dogs=user_dogs)
    return render(request, 'turns/ask_for_turn.html', {'form': form})

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def ViewPendingTurns(request):
    turnos = list(Turno.objects.filter(state="S").order_by('-hour', 'date')) # solicited
    return render(request, "turns/turn_list.html", {"turn_list" : turnos, "turns" : "P",
                                                    'turn_type_mapping': turn_type_mapping(), 'turn_hour_mapping': turn_hour_mapping()})

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def ViewAcceptedTurns(request):
    turnos = list(Turno.objects.filter(state="A").order_by('-hour', 'date')) # accepted
    return render(request, "turns/turn_list.html", {"turn_list" : turnos, "turns" : "A", "todays_date": date.today(),
                                                    'turn_type_mapping': turn_type_mapping(), 'turn_hour_mapping': turn_hour_mapping()})

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def AcceptTurn(request, turn_id):
    turn = Turno.objects.get(id=turn_id)
    turn.state = "A"
    turn.accepted_by = Veterinario.objects.get(user=request.user)
    turn.save()

    soliciter = get_user_model().objects.get(id=turn.solicited_by.id)
    message = 'Se ha aceptado su turno del %s en Oh My Dog' % turn.date.strftime('%d/%m/%Y')
    soliciter.email_user('Cambio en estado de turno', message)

    messages.success(request, "Turno aceptado")
    return redirect(reverse("pendingTurns"))

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def RejectTurn(request, turn_id):
    turn = Turno.objects.get(id=turn_id)

    soliciter = get_user_model().objects.get(id=turn.solicited_by.id)
    message = 'Se ha rechazado su turno del %s en Oh My Dog' % turn.date.strftime('%d/%m/%Y')
    soliciter.email_user('Cambio en estado de turno', message)

    turn.delete()

    messages.success(request, "Turno rechazado")
    return redirect(reverse("pendingTurns"))

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def ViewMyTurns(request):
    user = request.user
    dogs = Perro.objects.filter(owner=user)
    turnos = list(Turno.objects.filter(solicited_by__in=dogs).order_by('state', 'date', '-hour').exclude(state="F"))
    return render(request, "turns/turn_list.html", {"turn_list" : turnos, "turns" : "U",
                                                    'turn_type_mapping': turn_type_mapping(), 'turn_hour_mapping': turn_hour_mapping()})

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def CancelTurn(request, turn_id):
    turn = Turno.objects.get(id=turn_id).delete()

    soliciter = get_user_model().objects.get(id=turn.solicited_by.id)
    message = 'Usted ha cancelado su turno del %s en Oh My Dog' % turn.date.strftime('%d/%m/%Y')
    soliciter.email_user('Cambio en estado de turno', message)

    vet = request.user
    message = 'Se ha cancelado un turno del %s en Oh My Dog' % turn.date.strftime('%d/%m/%Y')
    vet.email_user('Cambio en estado de turno', message)

    messages.success(request, "Turno cancelado")
    return redirect(reverse("myTurns"))


@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def AttendTurnView(request, turn_id, urgency=False):
    turn = Turno.objects.get(id=turn_id)
    dog = turn.solicited_by
    if request.method == "POST":
        form = AttendTurnForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            Perro.objects.filter(id=dog.id).update(weight=weight)

            turn.observations = form.cleaned_data['observations']
            turn.amount = form.cleaned_data['amount']
            turn.state = 'F'
            turn.finalized_at = date.today()

            if turn.type == 'VA' or turn.type == 'VB':
                turn.add_to_health_book()

                # Automatic new vacunation turn
                new_date = generate_date(turn.date, dog.birthdate, type=turn.type)
                motive = f"Generación automática de turno para vacunación tipo {'A' if turn.type == 'VA' else 'B'}"
                Turno.objects.create(state='S', type=turn.type, hour=turn.hour, date=new_date, motive=motive, solicited_by=dog)

            elif turn.type == 'C':
                Perro.objects.filter(id=dog.id).update(castrated=True)
                turn.add_to_health_book()
            
            turn.save()
            turn.add_to_clinic_history()

            messages.success(request, "Turno finalizado")
            return redirect(reverse('home'))
        else:
            form.data = form.data.copy()
    else:
        form = AttendTurnForm(initial={'weight': dog.weight})
    return render(request, "turns/attend_turn.html", {'form': form, 'dog': dog})


@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def GenerateUrgencyView(request, dog_id):
    dog = Perro.objects.get(id=dog_id)
    turn = Turno.objects.create(type='U', hour=actual_turn_hour_check(), date=date.today(), motive='Urgencia',
                                solicited_by=dog, urgency_turns=json.dumps([]), accepted_by=Veterinario.objects.get(user=request.user))

    return redirect(reverse("attendUrgency", kwargs={"turn_id": turn.id}))

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def AttendUrgencyView(request, turn_id):
    turn = Turno.objects.get(id=turn_id)
    dog = turn.solicited_by
    if request.method == "POST":
        form = AttendTurnForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            Perro.objects.filter(id=dog.id).update(weight=weight)

            turn.observations = form.cleaned_data['observations']
            turn.amount = form.cleaned_data['amount']
            turn.state = 'F'

            turn.save()
            turn.add_to_health_book()
            turn.add_to_clinic_history()
            return redirect(reverse('home'))
        else:
            form.data = form.data.copy()
    else:
        form = AttendTurnForm(initial={'weight': dog.weight})
    return render(request, "turns/attend_turn.html", {'form': form, 'dog': dog, 'type': 'U', 'turn_id': turn.id})

@login_required(login_url='/login/')
@email_verification_required
@cache_control(max_age=3600, no_store=True)
def GenerateTurnForUrgencyView(request, turn_id, opt):
    turn = Turno.objects.get(id=turn_id)
    dog = turn.solicited_by
    if opt == 'VA' or opt == 'VB':
        # Generate vacunation turn
        motive = f"Vacunación tipo {'A' if opt == 'VA' else 'B'} inyectada en urgencia"
        vacc_turn = Turno.objects.create(state='F', type=opt, hour=turn.hour, date=turn.date, motive=motive, solicited_by=dog,
                                         accepted_by=Veterinario.objects.get(user=request.user), amount=0.0)
        vacc_turn.add_to_health_book()
        vacc_turn.add_to_clinic_history()

        # Automatic new vacunation turn ?
        new_date = generate_date(turn.date, dog.birthdate, type=turn.type)
        motive = f"Generación automática de turno para vacunación tipo {'A' if opt == 'VA' else 'B'} en urgencia"
        Turno.objects.create(state='S', type=opt, hour=turn.hour, date=new_date, motive=motive, solicited_by=dog)

    elif opt == 'C':
        # Generate castration turn
        motive = f"Castración realizada en urgencia"
        cast_turn = Turno.objects.create(state='F', type=opt, hour=turn.hour, date=turn.date, motive=motive, solicited_by=dog,
                                         accepted_by=Veterinario.objects.get(user=request.user), amount=0.0)
        cast_turn.add_to_health_book()
        cast_turn.add_to_clinic_history()

        # Update dog
        Perro.objects.filter(id=dog.id).update(castrated=True)

    # Add new intervention to urgency
    append_data(turn, opt)

    messages.success(request, "Intervención agregada")
    return redirect(reverse('attendUrgency', kwargs={"turn_id": turn.id}))