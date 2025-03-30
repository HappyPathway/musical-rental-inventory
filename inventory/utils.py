from django.utils import timezone
from .models import SearchLog

def log_search_query(request, query, app, results_count=0):
    """
    Log a search query to the database.
    
    Parameters:
    - request: The HttpRequest object
    - query: The search query string
    - app: Which app/section the search was performed in (e.g., 'inventory', 'rentals')
    - results_count: Number of results returned by the search
    
    Returns:
    - The created SearchLog instance
    """
    # Don't log empty queries
    if not query or query.strip() == '':
        return None
    
    # Create the search log entry
    search_log = SearchLog(
        query=query,
        app=app,
        results_count=results_count
    )
    
    # Add user information if available
    if request.user.is_authenticated:
        search_log.user = request.user
    
    # Get client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    search_log.ip_address = ip_address
    search_log.save()
    
    return search_log