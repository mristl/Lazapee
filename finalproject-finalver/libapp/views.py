from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Book, User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
import time

def merge_sort(arr, key_func): #sorting criteria
    if len(arr) <= 1: #if list contains 1 or 0 elements
        return arr
    
    mid = len(arr) // 2 #array divided into 2, index
    left_half = merge_sort(arr[:mid], key_func) #create left half by slicing, then sorted until  divided into single-element arrays
    right_half = merge_sort(arr[mid:], key_func)

    return merge(left_half, right_half, key_func) #after both halves have been sorted, combine both halves

def merge(left, right, key_func):
    sorted_list = []
    
    while left and right: #loop until both halves are empty
        left_key = key_func(left[0]).lower() if isinstance(key_func(left[0]), str) else key_func(left[0])
        right_key = key_func(right[0]).lower() if isinstance(key_func(right[0]), str) else key_func(right[0])
        
        if left_key <= right_key: #if left key is less than or equal to right key
            sorted_list.append(left.pop(0)) #add left element to sorted list
        else:
            sorted_list.append(right.pop(0)) #add right element to sorted list
    
    sorted_list.extend(left) #add remaining elements to the end
    sorted_list.extend(right)
    
    return sorted_list

def quick_sort(arr, key_func): #FOR MERGE SORT COMPLEXITY ANALYSIS PURPOSES ONLY
    
    if len(arr) <= 1:
        return arr

    pivot = arr[0] #first element
    left = [x for x in arr[1:] if key_func(x) <= key_func(pivot)] #create subarray containing elements where key_func result is less than or equal to pivot
    right = [x for x in arr[1:] if key_func(x) > key_func(pivot)]

    return quick_sort(left, key_func) + [pivot] + quick_sort(right, key_func)

def binary_search(arr, key, key_attr): #partial implementation can be done by checking neighbors
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

    # Pagination
    paginator = Paginator(available_books, 10)
    page_number = request.GET.get('page')
    book_list = paginator.get_page(page_number)


    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        user_id = request.POST.get('user_id')   

        try:
            # Perform binary search for user
            user = binary_search(all_users, user_id, 'id_number')
            if user is None:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'ID number not found.'
                })

            # Borrow limit check
            borrow_limit = 1 if user.user_type == 'Student' else 2
            borrowed_books_count = Book.objects.filter(status='borrowed', user=user).count()

            if borrowed_books_count >= borrow_limit:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'Borrower exceeded borrow limit.'
                })

            start_time = time.perf_counter()  # Record the start time
            # Perform binary search for the book
            book = binary_search(available_books, accession_number, 'accession_number')
            end_time = time.perf_counter()  # Record the end time for binary search
            user_search_time = end_time - start_time  # Calculate the elapsed time for user search
            # Print the elapsed time for user search
            print(f"User search time: {user_search_time:.10f} seconds")

            if book is None:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'Book not found or currently borrowed.'
                })
            
            

            # Borrow the book
            if book.status == 'available':
                book.status = 'borrowed'
                book.date_borrowed = timezone.now()
                book.user = user
                book.save()

                messages.success(
                    request,
                    f"Successfully borrowed: {book.title} by {book.author} (Accession No: {book.accession_number})"
                )
                
                return redirect('view_books')
    

        except Exception as e:
            return render(request, 'libapp/borrow_book.html', {
                'book_list': book_list,
                'error': str(e)
            })
        
    return render(request, 'libapp/borrow_book.html', {'book_list': book_list})

def linear_search(books, query, key_func):
    matched_books = []

    for book in books:
        if query.lower() in key_func(book).lower():
            matched_books.append(book)

    return matched_books

def view_books(request):
    borrowed_books = Book.objects.filter(status__in=['borrowed', 'overdue']).select_related('user')
    current_date = timezone.now().date()

    # capture sorting criteria
    sort_field = request.GET.get('sort', 'days_remaining')
    start_time = time.time()

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
    
    end_time = time.time()
    sorting_time = end_time - start_time
    print(f"Time taken to sort books: {sorting_time:.4f} seconds")

        
    # Apply linear search if a query is present
    search_query = request.GET.get('search', '')
    if search_query:
        borrowed_books = linear_search(
        borrowed_books,
        search_query,
        key_func=lambda book: f"{book.title} {book.author} {book.publisher} {book.user.name}"
    )

    # Calculate return dates, expected return dates, and days remaining
    overdue_books = []
    for book in borrowed_books:
        if book.days_remaining is not None and book.days_remaining < 0:  # Overdue
            book.status = 'overdue'
            fine = abs(book.days_remaining) * 5  # 5 pesos per day
            overdue_books.append({
                'accession_number': book.accession_number,
                'title': book.title,
                'fine': fine,
                'user': book.user.name
            })
        else:
            book.status = 'borrowed'

    # Pagination
    paginator = Paginator(borrowed_books, 15)
    page_number = request.GET.get('page')
    view_list = paginator.get_page(page_number)

    return render(request, 'libapp/view_books.html', {
        'view_list': view_list,
        'search_query': search_query,
        'sort_field': sort_field,
        'current_date': current_date,
    })


def return_book(request):
    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        try:
            book = Book.objects.get(accession_number__iexact=accession_number)

            # Check if the book is overdue
            if book.status == 'overdue':
                fine = abs(book.days_remaining) * 5  # Example fine: 5 pesos per day
                return render(request, 'libapp/confirm_return.html', {
                    'book': book,
                    'fine': fine,
                })

            # Proceed with normal return for non-overdue books
            if book.status == 'borrowed':
                book.status = 'available'
                book.date_borrowed = None
                book.save()
                messages.success(request, f"The book '{book.title}' has been successfully returned.")

        except Book.DoesNotExist:
            messages.error(request, "The specified book does not exist.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return redirect('view_books')


def confirm_return(request, accession_number):
    try:
        book = Book.objects.get(accession_number__iexact=accession_number)

        # If POST, finalize the return
        if request.method == "POST":
            book.status = 'available'
            book.date_borrowed = None
            book.save()
            messages.success(request, f"The book '{book.title}' has been successfully returned with the fine paid.")
            return redirect('view_books')

        # Render confirmation page for overdue book
        fine = abs(book.days_remaining) * 5  # Example: 5 pesos per overdue day
        return render(request, 'libapp/confirm_return.html', {'book': book, 'fine': fine})

    except Book.DoesNotExist:
        messages.error(request, "The specified book does not exist.")
        return redirect('view_books')


def linear_search_timed(request): #FOR LINEAR SEARCH TIME COMPLEXITY ANALYSIS PURPOSES ONLY
    # Fetch users and available books from the database
    all_users = list(User.objects.all())
    available_books = list(Book.objects.filter(status='available'))

    # Sort users and books on every request
    all_users = merge_sort(all_users, key_func=lambda user: user.id_number)
    available_books = merge_sort(available_books, key_func=lambda book: book.accession_number)

    # Pagination
    paginator = Paginator(available_books, 10)
    page_number = request.GET.get('page')
    book_list = paginator.get_page(page_number)


    if request.method == "POST":
        accession_number = request.POST.get('accession_number')
        user_id = request.POST.get('user_id')   

        try:
            # Perform binary search for user
            user = binary_search(all_users, user_id, 'id_number')
            if user is None:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'ID number not found.'
                })

            # Borrow limit check
            borrow_limit = 1 if user.user_type == 'Student' else 2
            borrowed_books_count = Book.objects.filter(status='borrowed', user=user).count()

            if borrowed_books_count >= borrow_limit:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'Borrower exceeded borrow limit.'
                })

            start_time = time.perf_counter()  # Record the start time
            # Perform linear search for the book
            matched_books = linear_search(available_books, accession_number, key=lambda book: book.accession_number)            
            end_time = time.perf_counter()  # Record the end time for binary search
            user_search_time = end_time - start_time  # Calculate the elapsed time for user search
            # Print the elapsed time for user search
            print(f"User search time: {user_search_time:.10f} seconds")


            if not matched_books:
                return render(request, 'libapp/borrow_book.html', {
                    'book_list': book_list,
                    'error': 'Book not found or currently borrowed.'
                })

            # Get the first matched book
            book = matched_books[0]

            
            # Borrow the book
            if book.status == 'available':
                book.status = 'borrowed'
                book.date_borrowed = timezone.now()
                book.user = user
                book.save()

                messages.success(
                    request,
                    f"Successfully borrowed: {book.title} by {book.author} (Accession No: {book.accession_number})"
                )
                
                return redirect('view_books')
    

        except Exception as e:
            return render(request, 'libapp/borrow_book.html', {
                'book_list': book_list,
                'error': str(e)
            })
        
    return render(request, 'libapp/borrow_book.html', {'book_list': book_list})