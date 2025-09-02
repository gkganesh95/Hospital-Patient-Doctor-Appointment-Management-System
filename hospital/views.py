from django.shortcuts import render, redirect, get_object_or_404
from .models import Doctor, Patient, Appointment
from .forms import PatientForm, AppointmentForm
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import now
from django.db.models import Count, Q

# Patient Registration
def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient registered')
            return redirect('book_appointment')
    else:
        form = PatientForm()
    return render(request, 'hospital/patient_form.html', {'form': form})

# Appointment Booking
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.appointment_datetime = datetime.combine(
                form.cleaned_data['appointment_date'], form.cleaned_data['appointment_time']
            )
            obj.save()
            messages.success(request, 'Appointment booked')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'hospital/appointment_form.html', {'form': form})

# Appointment List + Filtering
def appointment_list(request):
    department = request.GET.get('department')
    doctor_id = request.GET.get('doctor')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    appointments = Appointment.objects.select_related('doctor', 'patient').all()
    if department:
        appointments = appointments.filter(doctor__department=department)
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)
    if status:
        appointments = appointments.filter(status=status)
    if start_date and end_date:
        appointments = appointments.filter(appointment_datetime__date__range=[start_date, end_date])

    doctors = Doctor.objects.all()
    return render(request, 'hospital/appointment_list.html', {
        'appointments': appointments,
        'doctors': doctors,
        'DEPARTMENTS': Doctor.DEPARTMENT_CHOICES,
    })

# Appointment Edit/Reschedule
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.appointment_datetime = datetime.combine(
                form.cleaned_data['appointment_date'], form.cleaned_data['appointment_time']
            )
            obj.save()
            messages.success(request, 'Appointment updated')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment, initial={
            'appointment_date': appointment.appointment_datetime.date(),
            'appointment_time': appointment.appointment_datetime.time(),
        })
    return render(request, 'hospital/appointment_form.html', {'form': form, 'edit': True})

# Appointment Delete
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted')
        return redirect('appointment_list')
    return render(request, 'hospital/confirm_delete.html', {'object': appointment})

# Update Appointment Status
def update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Appointment.STATUS_CHOICES):
            appointment.status = status
            appointment.save()
            messages.success(request, f'Status updated to {status}')
        return redirect('appointment_list')
    return render(request, 'hospital/update_status.html', {'object': appointment})

# Dashboard View
def dashboard(request):
    today = now().date()  # current date

    total_patients = Patient.objects.count()
    total_appointments_today = Appointment.objects.filter(appointment_datetime__date=today).count()

    # Count completed and cancelled appointments overall or optionally for today
    appointment_status_counts = Appointment.objects.aggregate(
        completed=Count('id', filter=Q(status='Completed')),
        cancelled=Count('id', filter=Q(status='Cancelled'))
    )

    context = {
        'total_patients': total_patients,
        'total_appointments_today': total_appointments_today,
        'completed_appointments': appointment_status_counts['completed'],
        'cancelled_appointments': appointment_status_counts['cancelled'],
    }
    return render(request, 'hospital/dashboard.html', context)


