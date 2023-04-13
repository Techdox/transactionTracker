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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    transactions = AmexTransaction.objects.all()
    form = DateRangeFilterForm(request.POST or None)

    if request.POST.get('form_submitted'):
        if form.is_valid():
            # Filter the transactions based on the date range
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            transactions = transactions.filter(date__range=(start_date, end_date))
            
    elif request.GET.get('reset'):
        # Reset the form fields and the transactions
        form = DateRangeFilterForm()
        transactions = AmexTransaction.objects.all()

    # Calculate the sum of reimbursable transactions
    reimbursable_sum = AmexTransaction.objects.filter(reimbursable=True).aggregate(Sum('amount'))['amount__sum']

    non_reimbursable_sum = AmexTransaction.objects.filter(reimbursable=False).aggregate(Sum('amount'))['amount__sum']

    lifestyle_transactions = transactions.filter(category='lifestyle')
    lifestyle_sum = lifestyle_transactions.aggregate(Sum('amount'))['amount__sum']

    bills_transactions = transactions.filter(category='bills')
    bills_sum = bills_transactions.aggregate(Sum('amount'))['amount__sum']

    food_transactions = transactions.filter(category='food')
    food_sum = food_transactions.aggregate(Sum('amount'))['amount__sum']

    fuel_transactions = transactions.filter(category='fuel')
    fuel_sum = fuel_transactions.aggregate(Sum('amount'))['amount__sum']

    transport_transactions = transactions.filter(category='transport')
    transport_sum = transport_transactions.aggregate(Sum('amount'))['amount__sum']

    other_transactions = transactions.filter(category='other')
    other_sum = other_transactions.aggregate(Sum('amount'))['amount__sum']

    total_transactions = transactions
    total_sum = total_transactions.aggregate(Sum('amount'))['amount__sum']

    if non_reimbursable_sum is not None:
        budget_left = 900 - non_reimbursable_sum
    else:
        budget_left = 900

    return render(request, 'transactions_list.html', 
    {'transactions': transactions,
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


