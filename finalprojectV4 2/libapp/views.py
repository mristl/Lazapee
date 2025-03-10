from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Book
from django.contrib import messages

def borrow_book(request):
    # Fetch available books
    available_books = Book.objects.filter(status='available')
        
    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        
        try:
            # Case insensitive lookup for book by accession number
            book = Book.objects.get(accession_number__iexact=accession_number)    
            
            if book.status == 'available':
                # If book is available, mark it as borrowed and update other details
                book.status = 'borrowed'
                book.date_borrowed = timezone.now()  # Set the borrow date
                book.days_remaining = 5  # Set the borrow duration (in days)
                book.save()
                
                # Redirect to the "view books" page or other success page
                return redirect('view books')  
            else:
                # If book is already borrowed, show an error message
                return render(request, 'libapp/borrow_book.html', {
                    'available_books': available_books,
                    'error': 'This book is already borrowed.'
                })
        
        except Book.DoesNotExist:
            # If the book with the provided accession number does not exist
            return render(request, 'libapp/borrow_book.html', {
                'available_books': available_books,
                'error': 'Invalid accession number.'
            })
        
    # Always pass available books to the template
    return render(request, 'libapp/borrow_book.html', {'available_books': available_books})

def linear_search(books, query, key=lambda book: book.title):
    """
    Linear search implementation to search for books by the specified key (e.g., title, author, publisher).
    Returns all books that partially match the search query.
    """
    matched_books = []

    # Traverse through the list of books
    for book in books:
        # Check if the query is a substring of the current book's key (case insensitive)
        if query.lower() in key(book).lower():
            matched_books.append(book)

    return matched_books


def merge_sort(books, key_func):
    """
    MergeSort implementation for sorting the books based on a key function (e.g., title, author, publisher, or expected return date).
    This function recursively divides the array and merges the sorted parts back together.
    """
    if len(books) <= 1:
        return books
    
    # Split the books list into two halves
    mid = len(books) // 2
    left_half = merge_sort(books[:mid], key_func)
    right_half = merge_sort(books[mid:], key_func)

    # Merge the sorted halves
    return merge(left_half, right_half, key_func)

def merge(left, right, key_func):
    """
    Merges two sorted lists into one sorted list based on the provided key function.
    """
    sorted_list = []
    
    while left and right:
        # Ensure that we're handling strings and numeric fields separately
        left_key = key_func(left[0])
        right_key = key_func(right[0])
        
        # Compare as strings if the field is a string, else directly compare the numeric or date values
        if isinstance(left_key, str):
            left_key = left_key.lower()
        if isinstance(right_key, str):
            right_key = right_key.lower()
        
        if left_key <= right_key:
            sorted_list.append(left.pop(0))
        else:
            sorted_list.append(right.pop(0))
    
    # Append the remaining elements
    sorted_list.extend(left)
    sorted_list.extend(right)
    
    return sorted_list


def view_books(request):
    # Fetch all borrowed books
    borrowed_books = Book.objects.filter(status__in=['borrowed', 'overdue'])
    current_date = timezone.now().date()

    # Calculate expected return dates for each book
    for book in borrowed_books:
        if book.date_borrowed:
            book.expected_return_date = book.date_borrowed + timedelta(days=book.days_remaining)
        else:
            book.expected_return_date = None

    # Sorting criteria: title, author, publisher, days_remaining, or expected_return_date
    sort_field = request.GET.get('sort', 'title')

    if sort_field == 'title':
        borrowed_books = merge_sort(borrowed_books, key_func=lambda book: book.title)
    elif sort_field == 'author':
        borrowed_books = merge_sort(borrowed_books, key_func=lambda book: book.author)
    elif sort_field == 'publisher':
        borrowed_books = merge_sort(borrowed_books, key_func=lambda book: book.publisher)
    elif sort_field == 'days_remaining':
        borrowed_books = merge_sort(borrowed_books, key_func=lambda book: book.days_remaining)
    elif sort_field == 'accession_number':
        borrowed_books = merge_sort(borrowed_books, key_func=lambda book: book.accession_number)
    
    # Apply linear search if a search query is present
    search_query = request.GET.get('search', '')
    if search_query:
        search_query_lower = search_query.lower()
        borrowed_books = [
            book for book in borrowed_books
            if search_query_lower in book.title.lower() or
               search_query_lower in book.author.lower() or
               search_query_lower in book.publisher.lower()
        ]

    # Reset button functionality
    if 'reset' in request.GET:
        return redirect('view_books')  # Redirect to show all borrowed books

    # Calculate return dates and days remaining
    for book in borrowed_books:
        if book.date_borrowed:
            book.return_date = book.date_borrowed + timedelta(days=book.days_remaining)
        else:
            book.return_date = None

        # Calculate the return date as date_borrowed + 5 days
        return_date = (book.date_borrowed + timedelta(days=5)).date()
        days_left = (return_date - current_date).days
        book.days_remaining = max(days_left, 0)

        if days_left <= 0:
            book.status = 'overdue'

        book.save()

    return render(request, 'libapp/view_books.html', {
        'books': borrowed_books,
        'search_query': search_query,
        'sort_field': sort_field,
    })




def return_book(request):
    if request.method == "POST":
        accession_number = request.POST.get('accession_number')  
        try:
            book = Book.objects.get(accession_number__iexact=accession_number)
            if book.status in ['borrowed', 'overdue']:
                book.status = 'available'
                book.date_borrowed = None
                book.days_remaining = 0
                book.save()
                messages.success(request, f"The book '{book.title}' has been successfully returned.")
        except Book.DoesNotExist:
            messages.error(request, "The specified book does not exist.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    return redirect('view books')





def filtering(request):
    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        book = Book.objects.get(accession_number__iexact=accession_number)
        books = []

        if book.status == "available":
            books = books.append
        elif book.status == "borrowed":
            books = books.append
        else:
            books = books.append
            
        print(books)

        return render(request, 'libapp/view_books.html')
    

def descending_sorting(request, days_remaining):
    if request.method == "POST":
        days_remaining = request.POST.get('days_remaining')
       
    n = len(days_remaining)
    for i in range(n):
        swap_counter = 0
        for j in range(0, n - i - 1):
            if days_remaining[j] > days_remaining[j + 1]:
                days_remaining[j], days_remaining[j + 1] = days_remaining[j + 1], days_remaining[j]
                swap_counter += 1
            if swap_counter == 0:
                break
    return render(request, 'libapp/view_books.html')

def ascending_sorting(request, days_remaining):
    if request.method == "POST":
        days_remaining = request.POST.get('days_remaining')
       
    n = len(days_remaining)
    for i in range(n):
        swap_counter = 0
        for j in range(0, n - i - 1):
            if days_remaining[j] < days_remaining[j + 1]:
                days_remaining[j], days_remaining[j + 1] = days_remaining[j + 1], days_remaining[j]
                swap_counter += 1
            if swap_counter == 0:
                break
    return render(request, 'libapp/view_books.html')

