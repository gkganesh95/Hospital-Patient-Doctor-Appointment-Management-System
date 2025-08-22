from django import forms
from .models import Patient, Appointment
from datetime import datetime

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'

    def clean_age(self):
        age = self.cleaned_data['age']
        if age <= 0:
            raise forms.ValidationError("Age must be greater than 0")
        return age

    def clean_contact_number(self):
        num = self.cleaned_data['contact_number']
        if not num.isdigit() or len(num) != 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number")
        return num

class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time']

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        if doctor and appointment_date:
            day = appointment_date.strftime('%a')
            available_days = doctor.availability.split(',')
            if day not in available_days:
                raise forms.ValidationError("Doctor is not available on selected day.")

            # Check for slot 
            dt = datetime.combine(appointment_date, appointment_time)
            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_datetime=dt,
                status='Scheduled'
            ).exists()
            if exists:
                raise forms.ValidationError("This time slot is already booked for this doctor.")

        return cleaned_data
