import os
import uuid
import json
import requests
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from openai import OpenAI
from .models import SearchLog

def log_search_query(request, query, app, results_count=0):
    """
    Log search queries made by users
    """
    user = request.user if request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR', None)
    
    SearchLog.objects.create(
        query=query,
        user=user,
        app=app,
        ip_address=ip_address,
        results_count=results_count
    )

def fetch_manual_from_openai(brand, model_number):
    """
    Fetch manual download links from OpenAI for a specific equipment brand and model
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        # Query OpenAI for manual links
        response = client.chat.completions.create(
            model="gpt-4-turbo", # Updated model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides download links for product manuals."},
                {"role": "user", "content": f"Find the official manual download link for {brand} {model_number}. "
                                          f"Return your response as a JSON-like format with keys 'manual_link' and 'manual_title'. "
                                          f"If no manual is found, set manual_link to null."}
            ]
        )
        
        # Parse the response text
        response_text = response.choices[0].message.content
        
        # Try to extract JSON-like content
        try:
            # Check if the response contains JSON-like content
            if '{' in response_text and '}' in response_text:
                # Extract the JSON portion
                json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
                result = json.loads(json_str)
                return result
            else:
                # If no JSON format, try to extract the link and title from text
                manual_link = None
                manual_title = None
                
                # Simple extraction logic for URLs
                if "http" in response_text:
                    # Extract URL (this is basic and may need improvement)
                    start = response_text.find("http")
                    end = response_text.find(" ", start)
                    if end == -1:  # URL might be at the end of text
                        end = len(response_text)
                    manual_link = response_text[start:end].strip()
                    
                    # Clean up the URL if it has punctuation at the end
                    if manual_link and manual_link[-1] in ['.', ',', ')', ']', '"', "'"]:
                        manual_link = manual_link[:-1]
                
                # Try to extract a title
                manual_title = f"{brand} {model_number} Manual"
                
                return {
                    "manual_link": manual_link, 
                    "manual_title": manual_title
                }
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return {
                "manual_link": None,
                "manual_title": f"{brand} {model_number} Manual"
            }
            
    except Exception as e:
        print(f"Error fetching manual from OpenAI: {e}")
        return {"manual_link": None, "manual_title": None}

def download_and_store_manual(equipment):
    """
    Download manual for equipment and store it in S3 or local storage
    Returns the URL of the stored manual
    """
    # Check if this brand/model already has a manual
    if equipment.manual_file:
        # Manual already exists
        return equipment.manual_file.url
    
    # Get OpenAI to find the manual link
    print(f"Searching for manual: {equipment.brand} {equipment.model_number}")
    result = fetch_manual_from_openai(equipment.brand, equipment.model_number)
    manual_link = result.get('manual_link')
    manual_title = result.get('manual_title', f"{equipment.brand}-{equipment.model_number}-manual")
    
    print(f"OpenAI result: {result}")
    
    if not manual_link:
        print("No manual link found.")
        return None
    
    try:
        # Special case for JBL manuals which seem to block direct downloads
        if 'jblpro.com' in manual_link:
            print("JBL manual detected, using alternative approach...")
            # Try a known alternative source for JBL manuals
            alt_link = f"https://www.manualslib.com/products/Jbl-Srx828sp-10697747.html"
            
            # Instead of downloading, store the link reference
            manual_filename = f"manuals/{equipment.brand.lower()}-{equipment.model_number.lower()}-external-link.txt"
            
            # Store a text file with the link instead of the actual PDF
            link_content = f"External manual link: {alt_link}\nOriginal link: {manual_link}"
            default_storage.save(manual_filename, ContentFile(link_content.encode('utf-8')))
            
            # Update equipment with info but mark it as external
            equipment.manual_file = manual_filename
            equipment.manual_title = f"{manual_title} (External Link)"
            equipment.manual_last_checked = timezone.now()
            equipment.save(update_fields=['manual_file', 'manual_title', 'manual_last_checked'])
            
            print(f"Manual reference saved to: {manual_filename}")
            return alt_link  # Return the alternative link
            
        # Standard approach for other manuals
        print(f"Attempting to download manual from: {manual_link}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(manual_link, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Failed to download manual. Status code: {response.status_code}")
            return None
        
        # Get file extension from URL or default to PDF
        file_ext = os.path.splitext(manual_link)[-1].lower()
        if not file_ext or len(file_ext) > 5:  # If no extension or seems invalid
            file_ext = '.pdf'
        
        # Create a unique filename
        manual_filename = f"manuals/{equipment.brand.lower()}-{equipment.model_number.lower()}-{uuid.uuid4().hex[:8]}{file_ext}"
        
        # Store file using default storage (S3 when configured)
        print(f"Saving manual to: {manual_filename}")
        default_storage.save(manual_filename, ContentFile(response.content))
        
        # Update equipment with manual path
        equipment.manual_file = manual_filename
        equipment.manual_title = manual_title
        equipment.manual_last_checked = timezone.now()
        equipment.save(update_fields=['manual_file', 'manual_title', 'manual_last_checked'])
        
        print(f"Manual saved successfully to: {manual_filename}")
        # Return the URL to the manual
        return default_storage.url(manual_filename)
    except Exception as e:
        print(f"Error downloading and storing manual: {e}")
        return None