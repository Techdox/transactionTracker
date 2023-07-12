# Create your views here.
from unicodedata import category
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AmexTransactionForm, DateRangeFilterForm
from .models import AmexTransaction
from django.db.models import Sum
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.views.generic import ListView
from django.core.paginator import Paginator
# test

def home(request):
    return render(request, 'home.html')

def export_transactions_pdf(request):
    transactions = AmexTransaction.objects.all()
    context = {'transactions': transactions}
    template = 'pdf_export.html'
    html = render(request, template, context).content
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
        return response
    return HttpResponse('Error generating PDF', status=400)

def delete_transaction(request, pk):
    transaction = get_object_or_404(AmexTransaction, pk=pk)
    transaction.delete()
    return redirect('transactions_list')


def transactions_list(request):
    all_transactions = AmexTransaction.objects.all()
    form = DateRangeFilterForm(request.POST or None)

    if request.POST.get('form_submitted'):
        if form.is_valid():
            # Filter the transactions based on the date range
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            all_transactions = all_transactions.filter(date__range=(start_date, end_date))

    elif request.GET.get('reset'):
        # Reset the form fields and the transactions
        form = DateRangeFilterForm()
        all_transactions = AmexTransaction.objects.all()

    paginator = Paginator(all_transactions, 10)  # Show 10 transactions per page

    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)

    # Calculate the sum of reimbursable transactions
    reimbursable_sum = AmexTransaction.objects.filter(reimbursable=True).aggregate(Sum('amount'))['amount__sum']
    non_reimbursable_sum = AmexTransaction.objects.filter(reimbursable=False).aggregate(Sum('amount'))['amount__sum']

    lifestyle_transactions = all_transactions.filter(category='lifestyle')
    lifestyle_sum = lifestyle_transactions.aggregate(Sum('amount'))['amount__sum']

    bills_transactions = all_transactions.filter(category='bills')
    bills_sum = bills_transactions.aggregate(Sum('amount'))['amount__sum']

    food_transactions = all_transactions.filter(category='food')
    food_sum = food_transactions.aggregate(Sum('amount'))['amount__sum']

    fuel_transactions = all_transactions.filter(category='fuel')
    fuel_sum = fuel_transactions.aggregate(Sum('amount'))['amount__sum']

    transport_transactions = all_transactions.filter(category='transport')
    transport_sum = transport_transactions.aggregate(Sum('amount'))['amount__sum']

    other_transactions = all_transactions.filter(category='other')
    other_sum = other_transactions.aggregate(Sum('amount'))['amount__sum']

    total_transactions = all_transactions
    total_sum = total_transactions.aggregate(Sum('amount'))['amount__sum']

    if non_reimbursable_sum is not None:
        budget_left = 900 - non_reimbursable_sum
    else:
        budget_left = 900

    return render(request, 'transactions_list.html', {
        'transactions': transactions,
        'form': form,
        'reimbursable_sum': reimbursable_sum,
        'non_reimbursable_sum': non_reimbursable_sum,
        'lifestyle_sum': lifestyle_sum,
        'bills_sum': bills_sum,
        'food_sum': food_sum,
        'fuel_sum': fuel_sum,
        'transport_sum': transport_sum,
        'other_sum': other_sum,
        'total_sum': total_sum,
        'budget_left': budget_left,
    })


def create_transaction(request):
    # If this is a POST request, we are processing a form submission
    if request.method == 'POST':
        # Create a form instance and populate it with the POST data
        form = AmexTransactionForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Save the form data to the database
            form.save(commit=True)
            # Redirect to the transaction list page
            return redirect('transactions_list')
    # If this is a GET request (or any other method), we will create a blank form
    else:
        form = AmexTransactionForm()
    # Render the template with the form
    return render(request, 'transactions/create.html', {'form': form})


from django.shortcuts import render

from django.shortcuts import render

def budget_view(request):
    if request.method == 'POST':
        total_income = request.POST.get('total_income')
        bill_1 = request.POST.get('bill_1')
        bill_2 = request.POST.get('bill_2')

        # Validate inputs
        errors = []
        if not total_income:
            errors.append("Total monthly income is required.")

        # Filter out empty bill values
        bills = [float(bill) for bill in [bill_1, bill_2] if bill]

        if not bills:
            errors.append("At least one bill value is required.")

        if errors:
            return render(request, 'budget.html', {'errors': errors})

        # Perform calculations
        try:
            total_income = float(total_income)

            total_utilized = sum(bills)
            remaining_budget = total_income - total_utilized

            return render(request, 'budget.html', {
                'total_income': total_income,
                'bills': bills,
                'total_utilized': total_utilized,
                'remaining_budget': remaining_budget,
            })
        except ValueError:
            errors.append("Invalid input. Please enter numeric values for income and bills.")
            return render(request, 'budget.html', {'errors': errors})

    else:
        return render(request, 'budget.html')
