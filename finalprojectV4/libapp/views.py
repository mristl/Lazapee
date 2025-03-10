from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Book, User
from django.contrib import messages

def merge_sort(arr, key_func):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid], key_func)
    right_half = merge_sort(arr[mid:], key_func)

    return merge(left_half, right_half, key_func)

def merge(left, right, key_func):
    sorted_list = []
    
    while left and right:
        left_key = key_func(left[0]).lower() if isinstance(key_func(left[0]), str) else key_func(left[0])
        right_key = key_func(right[0]).lower() if isinstance(key_func(right[0]), str) else key_func(right[0])
        
        if left_key <= right_key:
            sorted_list.append(left.pop(0))
        else:
            sorted_list.append(right.pop(0))
    
    sorted_list.extend(left)
    sorted_list.extend(right)
    
    return sorted_list

def binary_search(arr, key, key_attr):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_key = getattr(arr[mid], key_attr).lower()  
        
        if mid_key == key.lower():
            return arr[mid]
        elif mid_key < key.lower():
            low = mid + 1
        else:
            high = mid - 1
    return None

def borrow_book(request):
    # Fetch users and available books from the database
    all_users = list(User.objects.all())
    available_books = list(Book.objects.filter(status='available'))
    
    # Sort users and books on every request
    all_users = merge_sort(all_users, key_func=lambda user: user.id_number)
    available_books = merge_sort(available_books, key_func=lambda book: book.accession_number)

    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        user_id = request.POST.get('user_id')

        try:
            # Perform binary search for user
            user = binary_search(all_users, user_id, 'id_number')
            if user is None:
                return render(request, 'libapp/borrow_book.html', {
                    'available_books': available_books,
                    'error': 'ID number not found.'
                })

            # Borrow limit check
            borrow_limit = 1 if user.user_type == 'Student' else 2
            borrowed_books_count = Book.objects.filter(status='borrowed', user=user).count()

            if borrowed_books_count >= borrow_limit:
                return render(request, 'libapp/borrow_book.html', {
                    'available_books': available_books,
                    'error': 'Borrower exceeded borrow limit.'
                })

            # Perform binary search for the book
            book = binary_search(available_books, accession_number, 'accession_number')
            if book is None:
                return render(request, 'libapp/borrow_book.html', {
                    'available_books': available_books,
                    'error': 'Book not found or currently borrowed.'
                })

            # Borrow the book
            if book.status == 'available':
                book.status = 'borrowed'
                book.date_borrowed = timezone.now()
                book.days_remaining = 5
                book.user = user
                book.save()

                return redirect('view_books')
    

        except Exception as e:
            return render(request, 'libapp/borrow_book.html', {
                'available_books': available_books,
                'error': str(e)
            })

    return render(request, 'libapp/borrow_book.html', {'available_books': available_books})

def linear_search(books, query, key=lambda book: book.title):
    matched_books = []

    for book in books:
        if query.lower() in key(book).lower():
            matched_books.append(book)

    return matched_books

def view_books(request):
    borrowed_books = Book.objects.filter(status__in=['borrowed', 'overdue'])
    current_date = timezone.now().date()

    # Sorting criteria
    sort_field = request.GET.get('sort', 'title')

    # Apply sorting based on selected field
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

    # Apply linear search if a query is present
    search_query = request.GET.get('search', '')
    if search_query:
        search_query_lower = search_query.lower()
        borrowed_books = [
            book for book in borrowed_books
            if search_query_lower in book.title.lower() or
               search_query_lower in book.author.lower() or
               search_query_lower in book.publisher.lower()
        ]


    # Calculate return dates, expected return dates, and days remaining
    for book in borrowed_books:
        if book.date_borrowed:
            # Calculate the return date (date_borrowed + 5 days)
            book.return_date = (book.date_borrowed + timedelta(days=5)).date()
            days_left = (book.return_date - current_date).days
            book.days_remaining = max(days_left, 0)

            if days_left <= 0:
                book.status = 'overdue'
            else:
                book.status = 'borrowed'
        else:
            # If no date_borrowed, handle gracefully
            book.return_date = None
            book.days_remaining = 0

        # Save only if necessary
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
    return redirect('view_books')
