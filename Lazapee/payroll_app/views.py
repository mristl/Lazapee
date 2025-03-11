from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip
from django.contrib import messages

# Create your views here.

def employees(request):
    employee_objects = Employee.objects.all()
    return render(request, 'payroll_app/employees.html', {'employees':employee_objects})

def payslip(request):
    payslip_objects = Payslip.objects.all()
    return render(request, 'payroll_app/payslip.html', {'payslip':payslip_objects})

def create_payslip(request):
    payslip_objects = Payslip.objects.all()
    employee_objects = Employee.objects.all()
    if request.method == "POST":
        id_number = request.POST.get('id_number')
        month = request.POST.get('month')
        year = request.POST.get('year')
        pay_cycle = request.POST.get('pay_cycle')
        date_range = ""
        deductions_tax = 0
        deductions_health = 0
        pag_ibig = 0
        sss = 0
        total_pay = 0
        if id_number == "All_Employees":
            for employee in employee_objects:
                if Payslip.objects.filter(id_number=employee, month=month, year=year, pay_cycle=pay_cycle).exists():
                    messages.warning(request, f"A payslip already exists for employee {employee.id_number}, {month} {year}, Cycle {pay_cycle}.")
                else:
                    employee_rate = employee.getRate()
                    earnings_allowance = employee.getAllowance()
                    overtime = employee.getOvertime()
                    if pay_cycle == "1":
                        date_range = "1-15"
                        pag_ibig = 100
                        deductions_tax = ((employee_rate / 2) + earnings_allowance + overtime - pag_ibig) * 0.2
                        total_pay = ((employee_rate / 2) + earnings_allowance + overtime - pag_ibig) - deductions_tax
                    else:
                        if month in ["January", "March", "May", "July", "August", "October", "December"]:
                            date_range = "16-31"
                        elif month in ["February"]:
                            date_range = "16-28"
                        elif month in ["April", "June", "September" , "November"]:
                            date_range = "16-30"
                        deductions_health = employee_rate * 0.04
                        sss = employee_rate * 0.045
                        deductions_tax = ((employee_rate / 2) + earnings_allowance + overtime - deductions_health - sss) * 0.2
                        total_pay = ((employee_rate / 2) + earnings_allowance + overtime - deductions_health - sss) - deductions_tax

                    Payslip.objects.create(
                    id_number=employee, 
                    month=month, 
                    date_range = date_range, 
                    year=year, 
                    pay_cycle=pay_cycle, 
                    rate=employee_rate, 
                    earnings_allowance = earnings_allowance, 
                    deductions_tax = deductions_tax, 
                    deductions_health = deductions_health, 
                    pag_ibig = pag_ibig, 
                    sss = sss, 
                    overtime = overtime, 
                    total_pay = total_pay)
                    employee.resetOvertime()
                    employee.save()
        else:
            employee = get_object_or_404(Employee, id_number=id_number)
            if Payslip.objects.filter(id_number=employee, month=month, year=year, pay_cycle=pay_cycle).exists():
                messages.warning(request, f"A payslip already exists for employee {employee.id_number}, {month} {year}, Cycle {pay_cycle}.")
            else:
                employee_rate = employee.getRate()
                earnings_allowance = employee.getAllowance()
                overtime = employee.getOvertime()
                if pay_cycle == "1":
                    date_range = "1-15"
                    pag_ibig = 100
                    deductions_tax = ((employee_rate/2) + earnings_allowance + overtime - pag_ibig) * 0.2
                    total_pay = ((employee_rate/2) + earnings_allowance + overtime - pag_ibig) - deductions_tax
                else:
                    if month in ["January", "March", "May", "July", "August", "October", "December"]:
                        date_range = "16-31"
                    elif month in ["February"]:
                        date_range = "16-28"
                    elif month in ["April", "June", "September" , "November"]:
                        date_range = "16-30"
                    deductions_health = employee_rate * 0.04
                    sss = employee_rate * 0.045
                    deductions_tax = ((employee_rate / 2) + earnings_allowance + overtime - deductions_health - sss) * 0.2
                    total_pay = ((employee_rate / 2) + earnings_allowance + overtime - deductions_health - sss) - deductions_tax
                    
                Payslip.objects.create(
                id_number=employee, 
                month=month, 
                date_range = date_range, 
                year=year, 
                pay_cycle=pay_cycle, 
                rate=employee_rate, 
                earnings_allowance = earnings_allowance, 
                deductions_tax = deductions_tax, 
                deductions_health = deductions_health, 
                pag_ibig = pag_ibig, 
                sss = sss, 
                overtime = overtime, 
                total_pay = total_pay)
                employee.resetOvertime()
                employee.save()
        return redirect('payslip')
    else:
        return render(request, 'payroll_app/payslip.html',  {'payslip':payslip_objects, 'employees':employee_objects})  

def view_payslip_detail(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    employee = payslip.id_number
    base_pay = payslip.rate / 2
    gross_pay = base_pay + payslip.earnings_allowance + payslip.overtime
    total_deductions_1 = payslip.deductions_tax + payslip.pag_ibig
    total_deductions_2 = payslip.deductions_tax + payslip.deductions_health + payslip.sss
    return render(request, 'payroll_app/view_payslip_detail.html', {'p': payslip,'e':employee, 'base_pay': base_pay, 'gross_pay': gross_pay, 'total_deductions_1': total_deductions_1, 'total_deductions_2': total_deductions_2})

def delete_payslip(request, pk):
    Payslip.objects.filter(pk=pk).delete()
    return redirect('payslip')

def create_employee(request):
    if request.method == "POST":
        name = request.POST.get('name')
        id_number = request.POST.get('id_number')
        rate = request.POST.get('rate')
        allowance = request.POST.get('allowance')

        if Employee.objects.filter(id_number=id_number).exists():
            messages.error(request, 'ID number already exists. Please try again.')
            return render(request, 'payroll_app/create_employee.html')
        else:
            if allowance == "":
                allowance = 0
            Employee.objects.create(name=name, id_number=id_number, rate=rate, allowance=allowance)
            return redirect('employees')
    else:
        return render(request, 'payroll_app/create_employee.html')
    
def delete_employee(request, pk):
    Employee.objects.filter(pk=pk).delete()
    return redirect('employees')
    
def update_employee(request, pk):
    if(request.method=="POST"):
        name = request.POST.get('name')
        id_number = request.POST.get('id_number')
        rate = request.POST.get('rate')
        allowance = request.POST.get('allowance')

        if allowance=="":
            allowance = 0

        Employee.objects.filter(pk=pk).update(name=name, rate=rate, allowance=allowance)
        return redirect('employees')
    else:
        e = get_object_or_404(Employee, pk=pk)
        return render(request, 'payroll_app/update_employee.html', {'e':e})
    
def add_overtime(request, pk):
    if(request.method=="POST"):
        overtime_hours = float(request.POST.get('hours'))
        e = get_object_or_404(Employee, pk=pk)
        e.calcOvertime(overtime_hours)
        e.save()
    return redirect('employees')

def reset_overtime(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.resetOvertime()
    employee.save()
    return redirect('employees')