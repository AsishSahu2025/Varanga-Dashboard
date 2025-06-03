from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MyUser
import ee
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Pond, Parameter # Adjust as per your app structure
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import MyUser


class SignupView(APIView):
    def post(self, request):
        data = request.data
        name = data.get('name')
        mob = data.get('Mob')
        email = data.get('Email')
        password = data.get('password')
        address = data.get('address', '')

        if not all([name, mob, email, password]):
            return Response({"error": "name, Mob, Email, and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if MyUser.objects.filter(Mob=mob).exists():
            return Response({"error": "Mobile number already registered"}, status=status.HTTP_400_BAD_REQUEST)
        if MyUser.objects.filter(Email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        user = MyUser.objects.create(
            name=name,
            Mob=mob,
            Email=email,
            password=password,
            address=address
        )
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

class SigninView(APIView):
    def post(self, request):
        data = request.data
        identifier = data.get('identifier')  # Email or mobile number
        password = data.get('password')

        if not all([identifier, password]):
            return Response({"error": "Email/Mob and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Identify user by mobile or email
            if identifier.isdigit():
                user = MyUser.objects.get(Mob=int(identifier))
            else:
                user = MyUser.objects.get(Email=identifier)

            if user.password == password:
                refresh = RefreshToken.for_user(user)

                # Manual serialization of the user object
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'Mob': user.Mob,
                    'Email': user.Email,
                    'address': user.address,
                }

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    **user_data
                })

            else:
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        except MyUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        


from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
 # Adjust if needed

@api_view(['POST'])
def update_user_password(request):
    data = JSONParser().parse(request)
    identifier = data.get('identifier')
    new_password = data.get('new_password')

    if not identifier or not new_password:
        return JsonResponse({'message': 'email_or_mobile and new_password are required'}, status=400)

    try:
        if identifier.isdigit():
            user = MyUser.objects.filter(Mob=int(identifier)).first()
        else:
            user = MyUser.objects.filter(Email=identifier).first()

        if not user:
            return JsonResponse({'message': 'User not found'}, status=404)

        user.password = new_password
        user.save()

        return JsonResponse({'message': 'Password updated successfully'}, status=200)
    
    except Exception as e:
        return JsonResponse({'message': 'Error updating password', 'error': str(e)}, status=500)




from django.views.decorators.csrf import csrf_exempt

from django.contrib.gis.geos import GEOSGeometry

@csrf_exempt
def add_pond(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)

            name = data.get('name')
            latlong = data.get('latlong')
            location_str = data.get('location')  # Example: "POINT(85.1234 20.1234)"
            area = data.get('area')
            address = data.get('address')
            user_id = data.get('user')  # This should be the Mob (primary key)

            if not all([name, latlong, location_str, address, user_id]):
                return JsonResponse({'message': 'Missing required fields'}, status=400)

            try:
                user = MyUser.objects.get(Mob=user_id)
            except MyUser.DoesNotExist:
                return JsonResponse({'message': 'User not found'}, status=404)

            # Convert string to GEOSGeometry
            location = GEOSGeometry(location_str)

            pond = Pond.objects.create(
                name=name,
                latlong=latlong,
                location=location,
                area=area,
                address=address,
                user=user
            )

            return JsonResponse({'message': 'Pond added successfully', 'pond_id': pond.id}, status=201)

        except Exception as e:
            return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Only POST method allowed'}, status=405)


def contact_info(request, mob):
    try:
        user = MyUser.objects.get(Mob=mob)
        data = {
            'name': user.name,
            'mobile': user.Mob,
            'email': user.Email,
            'address': user.address,
        }
        return JsonResponse(data, status=200)
    except MyUser.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=404)



from google.oauth2 import service_account 
SCOPES = ['https://www.googleapis.com/auth/earthengine.readonly']

credentials = service_account.Credentials.from_service_account_file(
    'ee-tapaskumarsahoo9090-6245e11643e0.json', scopes=SCOPES)  
ee.Initialize(credentials)

import random
from datetime import datetime, timedelta
def remote_sensing_data():
    try:
        ponds = Pond.objects.all()
        for pond in ponds:
            point_str = pond.latlong
            coordinates = point_str.strip("()").split(",")
            latitude, longitude = map(float, coordinates)
            geometry = ee.Geometry.Point([longitude, latitude])
            print("Geometry:", geometry.getInfo())

            # # # Define a broader time range for image selection
            # end_date = datetime.now()

            # # # Set start date to 1 month back
            # start_date = end_date - timedelta(days=30)

            # # # Format the dates as strings
            # start_date_str = start_date.strftime('%Y-%m-%d')
            # end_date_str = end_date.strftime('%Y-%m-%d')
            # # Define a specific past date for your analysis
            # # specific_date = datetime(2025, 3, 30)  # Example: March 15, 2024
            
            # # Set start date to 1 month before the specific date
            # # start_date = specific_date - timedelta(days=30)

            # # Format the dates as strings
            # # start_date_str = start_date.strftime('%Y-%m-%d')
            # # end_date_str = specific_date.strftime('%Y-%m-%d')

            # print(f"Fetching data from {start_date_str} to {end_date_str}")
            # # # Define a broader time range for image selection



            # end_date = datetime.now()

            # # Set start date to 1 month back
            # start_date = end_date - timedelta(days=30)

            # # Format the dates as strings
            # start_date_str = start_date.strftime('%Y-%m-%d')
            # end_date_str = end_date.strftime('%Y-%m-%d')
            # Define a specific past date for your analysis
            specific_date = datetime(2025, 5, 5)  # Example: March 15, 2024
            
            # Set start date to 1 month before the specific date
            start_date = specific_date - timedelta(days=30)

            # Format the dates as strings
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = specific_date.strftime('%Y-%m-%d')

            print(f"Fetching data from {start_date_str} to {end_date_str}")

            # Filter the image collection
            image_collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                .filterBounds(geometry) \
                .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 40)) \
                .filterDate(start_date, specific_date)

            # Get the count of available images
            image_count = image_collection.size().getInfo()
            print("Available images count:", image_count)

            # Check if there are any images available
            if image_count > 0:
                # Get the most recent image
                most_recent_image = image_collection.sort('system:time_start', False).first()
                image = ee.Image(most_recent_image)  # Ensure it's an ee.Image

            # Calculate 
            
            
            
            
            ph = ee.Image(8.339).subtract(ee.Image(0.827).multiply(image.select('B1').divide(image.select('B8')))).rename('pH')
            
            # Calculate Dissolved Oxygen
            dissolved_oxygen = ee.Image(-0.0167).multiply(image.select('B8')) \
                                .add(ee.Image(0.0067).multiply(image.select('B9'))) \
                                .add(ee.Image(0.0083).multiply(image.select('B11'))) \
                                .add(ee.Image(9.577)).rename('Dissolved_Oxygen')
            
            # Calculate NDVI (Normalized Difference Vegetation Index)
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            
            # Calculate NDTI (Normalized Difference Turbidity Index)
            ndti = image.normalizedDifference(['B4', 'B3']).rename('NDTI')
            
            # Calculate GCI (Green Chlorophyll Index)
            gci = image.select('B3').pow(0.5).multiply(image.select('B4')).pow(0.5).subtract(1).rename('GCI')
            
            # Calculate NDCI (Normalized Difference Chlorophyll Index)  
            ndci = (image.select('B5').subtract(image.select('B4'))).divide(image.select('B5').add(image.select('B4'))).rename('NDCI')
            
            # Calculate NDWI (Normalized Difference Water Index)
            ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
            
            # Calculate Total Suspended Solids (TSS)
            tss = image.select('B4').subtract(image.select('B8')).pow(2).multiply(0.6113).rename('TSS')
            
            # Calculate CDOM index
            cdom_index = image.select('B3').divide(image.select('B2')).rename('CDOM_Index')

            # Calculate Phycocyanin
            phycocyanin = ee.Image(26.89).multiply(image.select('B3').divide(image.select('B2'))).subtract(27.43).rename('Phycocyanin')
            
            # Chlorophyll-a Calculation using the formula Chl-a = (B5 + B6) / B4
            chl_a = image.select('B5').add(image.select('B6')).divide(image.select('B4')).rename('Chl-a')

            
            # Reduce the images to get the mean values
            ph_mean = ph.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('pH')
            dissolved_oxygen_mean = dissolved_oxygen.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Dissolved_Oxygen')
            ndvi_mean = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDVI')
            ndti_mean = ndti.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDTI')
            gci_mean = gci.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('GCI')
            ndci_mean = ndci.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDCI')
            ndwi_mean = ndwi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDWI')
            tss_mean = tss.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('TSS')
            cdom_mean = cdom_index.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('CDOM_Index')
            phycocyanin_mean = phycocyanin.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Phycocyanin')
            chl_a_mean = chl_a.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Chl-a')
            
            # Create a dictionary to store the data
            data = {
                'pH': ph_mean.getInfo(),
                'Dissolved Oxygen': dissolved_oxygen_mean.getInfo(),
                'NDVI': ndvi_mean.getInfo(),
                'NDTI': ndti_mean.getInfo(),
                'GCI': gci_mean.getInfo(),
                'NDCI': ndci_mean.getInfo(),
                'NDWI': ndwi_mean.getInfo(),
                'TSS': tss_mean.getInfo(),
                'CDOM': cdom_mean.getInfo(),
                'AQUATIC_MACROPYTES': ndvi_mean.getInfo(),  # You might want to reconsider this key as it's a repeat of NDVI
                'Phycocyanin': phycocyanin_mean.getInfo(),
                'Chl-a': chl_a_mean.getInfo()  # Correct key for Chlorophyll-a
            }
            
            # Save data to the database
            parameter = Parameter.objects.create(
                pond=pond,
                pH=data.get('pH'),
                dissolved_oxygen=data.get('Dissolved Oxygen'),
                NDVI=data.get('NDVI'),
                NDTI=data.get('NDTI'),
                GCI=data.get('GCI'),
                NDCI=data.get('NDCI'),
                NDWI=data.get('NDWI'),
                TSS=data.get('TSS'),
                CDOM=data.get('CDOM'),
                AQUATIC_MACROPYTES=data.get('AQUATIC_MACROPYTES'),
                Phycocyanin=data.get('Phycocyanin'),
                Chl_a=data.get('Chl-a'),  # Storing the Chlorophyll-a data
                created_at=specific_date
            )
            user_email = pond.user.Email
            email_subject = 'Remote Sensing Data Saved....'
            email_message = f"""
            Dear User,
                The remote sensing data saved for pond '{pond.latlong}'.

                Regards,
                Bariflolabs
                """
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER, 
                [user_email], 
                fail_silently=False,
            )
            
            print("Email sent to", user_email)

        return JsonResponse({'message': 'Data saved successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Record not found'}, status=404)
       

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from app1.models import Parameter

class ParameterListView(APIView):
    def get(self, request):
        data = []
        for param in Parameter.objects.select_related('pond').all():
            data.append({
                "pond_id": param.pond.id,
                "pond_latlong": param.pond.latlong,
                "pH": param.pH,
                "dissolved_oxygen": param.dissolved_oxygen,
                "NDVI": param.NDVI,
                "NDTI": param.NDTI,
                "GCI": param.GCI,
                "NDCI": param.NDCI,
                "NDWI": param.NDWI,
                "TSS": param.TSS,
                "CDOM": param.CDOM,
                "AQUATIC_MACROPYTES": param.AQUATIC_MACROPYTES,
                "Phycocyanin": param.Phycocyanin,
                "Chl_a": param.Chl_a,
                "created_at": param.created_at,
            })
        return Response(data)
    




# views.py
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from app1.models import Parameter

# @api_view(['POST'])
# def graph(request, id):
#     try:
#         jsondata = JSONParser().parse(request)
#         month = jsondata.get('month')

#         if not month:
#             return JsonResponse({'message': 'Month is required'}, status=400)

#         temp = Parameter.objects.filter(
#             pond=id,
#             created_at__month=month
#         ).order_by('-created_at')[:5]

#         if temp.exists():
#             ph_values = [param.pH for param in temp]
#             DO_values = [param.dissolved_oxygen for param in temp]
#             ndvi_values = [param.NDVI for param in temp]
#             ndti_values = [param.NDTI for param in temp]
#             gci_values = [param.GCI for param in temp]
#             ndci_values = [param.NDCI for param in temp]
#             ndwi_values = [param.NDWI for param in temp]
#             TSS_values = [param.TSS for param in temp]
#             cdom_values = [param.CDOM for param in temp]
#             AQUATIC_MACROPYTES_values = [param.AQUATIC_MACROPYTES for param in temp]
#             Chl_a_values = [param.Chl_a for param in temp]
#             Phycocyanin_values = [param.Phycocyanin for param in temp]

#             weeks = [f"week {(i.created_at.day - 1) // 7 + 1}" for i in temp]
#             weeks.reverse()

#             response = {
#                 'ph': ph_values,
#                 'dissolved_oxygen': DO_values,
#                 'NDVI': ndvi_values,
#                 'NDTI': ndti_values,
#                 'GCI': gci_values,
#                 'NDCI': ndci_values,
#                 'NDWI': ndwi_values,
#                 'TSS': TSS_values,
#                 'CDOM': cdom_values,
#                 'AQUATIC_MACROPYTES': AQUATIC_MACROPYTES_values,
#                 'Chl_a': Chl_a_values,
#                 'Phycocyanin': Phycocyanin_values,
#                 'week': weeks
#             }
#             return JsonResponse(response, safe=False)
#         else:
#             return JsonResponse({'message': 'No data found for the given month and pond'}, status=404)

#     except Exception as e:
#         return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)


from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from .models import Parameter  # Adjust import as needed

@api_view(['POST'])
def graph(request):
    try:
        jsondata = JSONParser().parse(request)
        month = jsondata.get('month')

        if not month:
            return JsonResponse({'message': 'Month is required'}, status=400)

        # Filter by month only (across all ponds or apply additional filters if needed)
        temp = Parameter.objects.filter(
            created_at__month=month
        ).order_by('-created_at')[:5]

        if not temp.exists():
            return JsonResponse({'message': 'No data found for the given month'}, status=404)

        response = {
            'ph': [param.pH for param in temp],
            'dissolved_oxygen': [param.dissolved_oxygen for param in temp],
            'NDVI': [param.NDVI for param in temp],
            'NDTI': [param.NDTI for param in temp],
            'GCI': [param.GCI for param in temp],
            'NDCI': [param.NDCI for param in temp],
            'NDWI': [param.NDWI for param in temp],
            'TSS': [param.TSS for param in temp],
            'CDOM': [param.CDOM for param in temp],
            'AQUATIC_MACROPYTES': [param.AQUATIC_MACROPYTES for param in temp],
            'Chl_a': [param.Chl_a for param in temp],
            'Phycocyanin': [param.Phycocyanin for param in temp],
            'week': [f"week {(p.created_at.day - 1) // 7 + 1}" for p in temp][::-1]  # Reverse for chronological order
        }

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

