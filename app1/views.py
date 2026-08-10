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
from django.db.models import (Case,When,Value,IntegerField,F,Window)
from django.db.models.functions import (ExtractDay,RowNumber)


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
    'fit-sanctum-502304-e4-4d8cd14377ff.json', scopes=SCOPES)  
ee.Initialize(credentials)

# import random
# from datetime import datetime, timedelta
# def remote_sensing_data():
#     try:
#         ponds = Pond.objects.all()
#         for pond in ponds:
#             point_str = pond.latlong
#             coordinates = point_str.strip("()").split(",")
#             latitude, longitude = map(float, coordinates)
#             geometry = ee.Geometry.Point([longitude, latitude])
#             print("Geometry:", geometry.getInfo())

#             # # Define a broader time range for image selection
#             # end_date = datetime.now()

#             # # Set start date to 1 month back
#             # start_date = end_date - timedelta(days=30)

#             # # Format the dates as strings
#             # start_date_str = start_date.strftime('%Y-%m-%d')
#             # end_date_str = end_date.strftime('%Y-%m-%d')
#             # Define a specific past date for your analysis
#             # specific_date = datetime(2025, 6, 26)  # Example: March 15, 2024
            
#             # Set start date to 1 month before the specific date
#             # start_date = specific_date - timedelta(days=30)

#             # Format the dates as strings
#             # start_date_str = start_date.strftime('%Y-%m-%d')
#             # end_date_str = specific_date.strftime('%Y-%m-%d')

#             # print(f"Fetching data from {start_date_str} to {end_date_str}")
#             # # Define a broader time range for image selection



#             # # end_date = datetime.now()

#             # # # Set start date to 1 month back
#             # # start_date = end_date - timedelta(days=30)

#             # # # Format the dates as strings
#             # # start_date_str = start_date.strftime('%Y-%m-%d')
#             # # end_date_str = end_date.strftime('%Y-%m-%d')
#             # # Define a specific past date for your analysis
#             # specific_date = datetime(2025, 5, 5)  # Example: March 15, 2024
            
#             # # Set start date to 1 month before the specific date
#             # start_date = specific_date - timedelta(days=30)

#             # # Format the dates as strings
#             # start_date_str = start_date.strftime('%Y-%m-%d')
#             # end_date_str = specific_date.strftime('%Y-%m-%d')

#             # print(f"Fetching data from {start_date_str} to {end_date_str}")

#             # Filter the image collection
#             image_collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
#                 .filterBounds(geometry)
#                 # .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 40)) \
#                 # .filterDate(start_date, specific_date)
#             print(image_collection.size().getInfo())

#             # Get the count of available images
#             image_count = image_collection.size().getInfo()
#             print("Available images count:", image_count)

#             # Check if there are any images available
#             if image_count > 0:
#                 # Get the most recent image
#                 most_recent_image = image_collection.sort('system:time_start', False).first()
#                 image = ee.Image(most_recent_image)  # Ensure it's an ee.Image

#             # Calculate 
            
            
            
            
#             ph = ee.Image(8.339).subtract(ee.Image(0.827).multiply(image.select('B1').divide(image.select('B8')))).rename('pH')
            
#             # Calculate Dissolved Oxygen
#             dissolved_oxygen = ee.Image(-0.0167).multiply(image.select('B8')) \
#                                 .add(ee.Image(0.0067).multiply(image.select('B9'))) \
#                                 .add(ee.Image(0.0083).multiply(image.select('B11'))) \
#                                 .add(ee.Image(9.577)).rename('Dissolved_Oxygen')
            
#             # Calculate NDVI (Normalized Difference Vegetation Index)
#             ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            
#             # Calculate NDTI (Normalized Difference Turbidity Index)
#             ndti = image.normalizedDifference(['B4', 'B3']).rename('NDTI')
            
#             # Calculate GCI (Green Chlorophyll Index)
#             gci = image.select('B3').pow(0.5).multiply(image.select('B4')).pow(0.5).subtract(1).rename('GCI')
            
#             # Calculate NDCI (Normalized Difference Chlorophyll Index)  
#             ndci = (image.select('B5').subtract(image.select('B4'))).divide(image.select('B5').add(image.select('B4'))).rename('NDCI')
            
#             # Calculate NDWI (Normalized Difference Water Index)
#             ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
            
#             # Calculate Total Suspended Solids (TSS)
#             tss = image.select('B4').subtract(image.select('B8')).pow(2).multiply(0.6113).rename('TSS')
            
#             # Calculate CDOM index
#             cdom_index = image.select('B3').divide(image.select('B2')).rename('CDOM_Index')

#             # Calculate Phycocyanin
#             phycocyanin = ee.Image(26.89).multiply(image.select('B3').divide(image.select('B2'))).subtract(27.43).rename('Phycocyanin')
            
#             # Chlorophyll-a Calculation using the formula Chl-a = (B5 + B6) / B4
#             chl_a = image.select('B5').add(image.select('B6')).divide(image.select('B4')).rename('Chl-a')

            
#             # Reduce the images to get the mean values
#             ph_mean = ph.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('pH')
#             dissolved_oxygen_mean = dissolved_oxygen.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Dissolved_Oxygen')
#             ndvi_mean = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDVI')
#             ndti_mean = ndti.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDTI')
#             gci_mean = gci.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('GCI')
#             ndci_mean = ndci.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDCI')
#             ndwi_mean = ndwi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('NDWI')
#             tss_mean = tss.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('TSS')
#             cdom_mean = cdom_index.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('CDOM_Index')
#             phycocyanin_mean = phycocyanin.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Phycocyanin')
#             chl_a_mean = chl_a.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10).get('Chl-a')
            
#             # Create a dictionary to store the data
#             data = {
#                 'pH': ph_mean.getInfo(),
#                 'Dissolved Oxygen': dissolved_oxygen_mean.getInfo(),
#                 'NDVI': ndvi_mean.getInfo(),
#                 'NDTI': ndti_mean.getInfo(),
#                 'GCI': gci_mean.getInfo(),
#                 'NDCI': ndci_mean.getInfo(),
#                 'NDWI': ndwi_mean.getInfo(),
#                 'TSS': tss_mean.getInfo(),
#                 'CDOM': cdom_mean.getInfo(),
#                 'AQUATIC_MACROPYTES': ndvi_mean.getInfo(),  # You might want to reconsider this key as it's a repeat of NDVI
#                 'Phycocyanin': phycocyanin_mean.getInfo(),
#                 'Chl-a': chl_a_mean.getInfo()  # Correct key for Chlorophyll-a
#             }
            
#             # Save data to the database
#             parameter = Parameter.objects.create(
#                 pond=pond,
#                 pH=data.get('pH'),
#                 dissolved_oxygen=data.get('Dissolved Oxygen'),
#                 NDVI=data.get('NDVI'),
#                 NDTI=data.get('NDTI'),
#                 GCI=data.get('GCI'),
#                 NDCI=data.get('NDCI'),
#                 NDWI=data.get('NDWI'),
#                 TSS=data.get('TSS'),
#                 CDOM=data.get('CDOM'),
#                 AQUATIC_MACROPYTES=data.get('AQUATIC_MACROPYTES'),
#                 Phycocyanin=data.get('Phycocyanin'),
#                 Chl_a=data.get('Chl-a'),  # Storing the Chlorophyll-a data
#                 # created_at=specific_date
#             )
#             # user_email = pond.user.Email
#             # email_subject = 'Remote Sensing Data Saved....'
#             # email_message = f"""
#             # Dear User,
#             #     The remote sensing data saved for pond '{pond.latlong}'.

#             #     Regards,
#             #     Bariflolabs
#             #     """
#             # send_mail(
#             #     email_subject,
#             #     email_message,
#             #     settings.EMAIL_HOST_USER, 
#             #     [user_email], 
#             #     fail_silently=False,
#             # )
            
#             # print("Email sent to", user_email)

#         return JsonResponse({'message': 'Data saved successfully'})
#     except Exception as e:
#         print(e)
#         return JsonResponse({'message': 'Record not found'}, status=404)
       

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

# @api_view(['POST'])
# def graph(request):
#     try:
#         jsondata = JSONParser().parse(request)
#         month = jsondata.get('month')
#         print(month)
#         print(jsondata)

#         if not month:
#             return JsonResponse({'message': 'Month is required'}, status=400)

#         # Filter by month only (across all ponds or apply additional filters if needed)
#         temp = Parameter.objects.filter(
#             created_at__month=month
#         ).order_by('-created_at')[:5]

#         if not temp.exists():
#             return JsonResponse({'message': 'No data found for the given month'}, status=404)

#         response = {
#             'ph': [param.pH for param in temp],
#             'dissolved_oxygen': [param.dissolved_oxygen for param in temp],
#             'NDVI': [param.NDVI for param in temp],
#             'NDTI': [param.NDTI for param in temp],
#             'GCI': [param.GCI for param in temp],
#             'NDCI': [param.NDCI for param in temp],
#             'NDWI': [param.NDWI for param in temp],
#             'TSS': [param.TSS for param in temp],
#             'CDOM': [param.CDOM for param in temp],
#             'AQUATIC_MACROPYTES': [param.AQUATIC_MACROPYTES for param in temp],
#             'Chl_a': [param.Chl_a for param in temp],
#             'Phycocyanin': [param.Phycocyanin for param in temp],
#             'week': [f"week {(p.created_at.day - 1) // 7 + 1}" for p in temp][::-1]  # Reverse for chronological order
#         }
#         print(response)

#         return JsonResponse(response, safe=False)

#     except Exception as e:
#         return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)




from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from .models import Parameter  # Adjust import as needed

# @api_view(['POST'])
# def graph(request):
#     try:
#         jsondata = JSONParser().parse(request)
#         month = jsondata.get("month")

#         # Validate month
#         if not month:
#             return JsonResponse(
#                 {"message": "Month is required"},
#                 status=400
#             )

#         try:
#             month = int(month)
#         except (TypeError, ValueError):
#             return JsonResponse(
#                 {"message": "Invalid month"},
#                 status=400
#             )

#         if month < 1 or month > 12:
#             return JsonResponse(
#                 {"message": "Month must be between 1 and 12"},
#                 status=400
#             )

#         # Get latest record of each week
#         records = (
#             Parameter.objects
#             .filter(created_at__month=month)
#             .annotate(
#                 day=ExtractDay("created_at")
#             )
#             .annotate(
#                 week=Case(
#                     When(day__lte=7, then=Value(1)),
#                     When(day__lte=14, then=Value(2)),
#                     When(day__lte=21, then=Value(3)),
#                     When(day__lte=28, then=Value(4)),
#                     default=Value(5),
#                     output_field=IntegerField(),
#                 )
#             )
#             .annotate(
#                 row_number=Window(
#                     expression=RowNumber(),
#                     partition_by=[F("week")],
#                     order_by=F("created_at").desc(),
#                 )
#             )
#             .filter(row_number=1)
#             .order_by("week")
#         )

#         if not records.exists():
#             return JsonResponse(
#                 {"message": "No data found for the given month"},
#                 status=404
#             )

#         # Easy lookup by week
#         weekly_map = {
#             record.week: record
#             for record in records
#         }

#         PARAMETER_FIELDS = {
#             "ph": "pH",
#             "dissolved_oxygen": "dissolved_oxygen",
#             "NDVI": "NDVI",
#             "NDTI": "NDTI",
#             "GCI": "GCI",
#             "NDCI": "NDCI",
#             "NDWI": "NDWI",
#             "TSS": "TSS",
#             "CDOM": "CDOM",
#             "AQUATIC_MACROPYTES": "AQUATIC_MACROPYTES",
#             "Chl_a": "Chl_a",
#             "Phycocyanin": "Phycocyanin",
#         }

#         response = {
#             key: []
#             for key in PARAMETER_FIELDS
#         }

#         response["week"] = []

#         for week in range(1, 6):
#             response["week"].append(f"week {week}")
#             record = weekly_map.get(week)

#             for response_key, model_field in PARAMETER_FIELDS.items():
#                 if record:
#                     response[response_key].append(
#                         getattr(record, model_field)
#                     )
#                 else:
#                     response[response_key].append(None)

#         return JsonResponse(response)

#     except Exception as e:
#         return JsonResponse(
#             {
#                 "message": "An error occurred",
#                 "error": str(e)
#             },
#             status=500
#         )




@api_view(["POST"])
def graph(request):
    try:
        jsondata = JSONParser().parse(request)

        month = jsondata.get("month")
        year = jsondata.get("year")

        # -----------------------------
        # Validate month
        # -----------------------------
        if month is None:
            return JsonResponse(
                {"message": "Month is required"},
                status=400
            )

        try:
            month = int(month)
        except (TypeError, ValueError):
            return JsonResponse(
                {"message": "Invalid month"},
                status=400
            )

        if month < 1 or month > 12:
            return JsonResponse(
                {"message": "Month must be between 1 and 12"},
                status=400
            )

        # -----------------------------
        # Validate year
        # -----------------------------
        if year is None:
            return JsonResponse(
                {"message": "Year is required"},
                status=400
            )

        try:
            year = int(year)
        except (TypeError, ValueError):
            return JsonResponse(
                {"message": "Invalid year"},
                status=400
            )

        
        # -----------------------------
        # Get latest record of each week
        # for the selected year + month
        # -----------------------------
        records = (
            Parameter.objects
            .filter(
                created_at__year=year,
                created_at__month=month
            )
            .annotate(
                day=ExtractDay("created_at")
            )
            .annotate(
                week=Case(
                    When(day__lte=7, then=Value(1)),
                    When(day__lte=14, then=Value(2)),
                    When(day__lte=21, then=Value(3)),
                    When(day__lte=28, then=Value(4)),
                    default=Value(5),
                    output_field=IntegerField(),
                )
            )
            .annotate(
                row_number=Window(
                    expression=RowNumber(),
                    partition_by=[F("week")],
                    order_by=F("created_at").desc(),
                )
            )
            .filter(row_number=1)
            .order_by("week")
        )

        if not records.exists():
            return JsonResponse(
                {
                    "message": "No data found for the given month and year"
                },
                status=404
            )

        # -----------------------------
        # Easy lookup by week
        # -----------------------------
        weekly_map = {
            record.week: record
            for record in records
        }

        # -----------------------------
        # Parameter mapping
        # -----------------------------
        PARAMETER_FIELDS = {
            # "ph": "pH",
            # "dissolved_oxygen": "dissolved_oxygen",
            # "NDVI": "NDVI",
            # "NDTI": "NDTI",
            # "GCI": "GCI",
            # "NDCI": "NDCI",
            # "NDWI": "NDWI",
            # "TSS": "TSS",
            # "CDOM": "CDOM",
            "AQUATIC_MACROPYTES": "AQUATIC_MACROPYTES",
            "Chl_a": "Chl_a",
            "Phycocyanin": "Phycocyanin",
        }

        response = {
            key: []
            for key in PARAMETER_FIELDS
        }

        response["week"] = []

        # -----------------------------
        # Return Week 1 to Week 5
        # -----------------------------
        for week in range(1, 6):

            response["week"].append(
                f"week {week}"
            )

            record = weekly_map.get(week)

            for response_key, model_field in PARAMETER_FIELDS.items():

                if record:
                    response[response_key].append(
                        getattr(record, model_field)
                    )
                else:
                    response[response_key].append(None)

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse(
            {
                "message": "An error occurred",
                "error": str(e)
            },
            status=500
        )






from datetime import datetime, timezone as dt_timezone
from django.http import JsonResponse
import ee
from .models import Pond, Parameter

def remote_sensing_data():
    try:
        ponds = Pond.objects.all()

        for pond in ponds:
            # ==================================================
            # 1. Create Earth Engine geometry
            # ==================================================

            point_str = pond.latlong
            coordinates = point_str.strip("()").split(",")
            latitude, longitude = map(float, coordinates)
            geometry = ee.Geometry.Point([longitude, latitude])

            print("Pond:", pond.id)
            print("Geometry:", geometry.getInfo())

            # ==================================================
            # 2. Get the last successfully processed image
            # ==================================================

            last_parameter = (Parameter.objects.filter(pond=pond,image_date__isnull=False)
                .order_by("-image_date")
                .first()
            )

            if last_parameter:
                print("Last processed image date:",last_parameter.image_date)
                print("Last processed image ID:",last_parameter.image_id)

            else:
                print("No previously processed Sentinel-2 image found.")

            # ==================================================
            # 3. Create Sentinel-2 ImageCollection
            # ==================================================

            image_collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
            )

            # ==================================================
            # 4. If we already processed an image,
            #    search only for newer images
            # ==================================================

            if last_parameter:
                last_image_date = last_parameter.image_date
                print("Searching for images after:",last_image_date)

                # Convert Django datetime to ISO format
                # Example:
                # 2026-08-03T00:05:24+00:00
                start_date = ee.Date(last_image_date.isoformat())

                # Current backend time
                current_date = timezone.now()

                # Convert current time to Earth Engine Date
                end_date = ee.Date(current_date.isoformat())

                image_collection = (image_collection.filterDate(start_date,end_date))

            # ==================================================
            # IMPORTANT:
            # Cloud filtering is intentionally NOT enabled yet.
            #
            # Do NOT uncomment this currently:
            #
            # .filter(
            #     ee.Filter.lte(
            #         'CLOUDY_PIXEL_PERCENTAGE',
            #         40
            #     )
            # )
            # ==================================================

            # ==================================================
            # 5. Count available new images
            # ==================================================

            image_count = (image_collection.size().getInfo())

            print("Available new Sentinel-2 images:",image_count)

            # ==================================================
            # 6. If there is no new image, skip this pond
            # ==================================================
            if image_count == 0:
                print(
                    f"No new Sentinel-2 image available "
                    f"for pond {pond.id}"
                )
                continue

            # ==================================================
            # 7. Select the latest available image
            # ==================================================

            most_recent_image = (image_collection.sort("system:time_start",False)
                .first()
            )

            image = ee.Image(most_recent_image)

            # ==================================================
            # 8. Get Sentinel-2 image metadata
            # ==================================================

            image_id = image.id().getInfo()
            image_timestamp = (image.get("system:time_start").getInfo())

            satellite_name = (image.get("SPACECRAFT_NAME").getInfo())
            cloud_percentage = (image.get("CLOUDY_PIXEL_PERCENTAGE").getInfo())

            # Earth Engine timestamp is milliseconds.
            # Convert it to timezone-aware Python datetime.
            image_date = datetime.fromtimestamp(image_timestamp / 1000,tz=dt_timezone.utc)

            print("\nSelected Sentinel-2 image:")
            print("Image ID:", image_id)
            print("Image date:", image_date)
            print("Satellite:", satellite_name)
            print("Cloud percentage:",cloud_percentage)

            # ==================================================
            # 9. Check whether this exact image was already
            #    processed for this pond
            # ==================================================

            already_processed = (Parameter.objects.filter(pond=pond,image_id=image_id).exists())

            if already_processed:
                print("Image already processed:",image_id)
                continue

            # ==================================================
            # 10. EXISTING PARAMETER CALCULATIONS
            #
            # IMPORTANT:
            # These formulas are kept unchanged.
            # ==================================================

            # Calculate pH
            ph = (ee.Image(8.339).subtract(ee.Image(0.827).multiply(image.select("B1").divide(image.select("B8")))).rename("pH"))

            # Calculate Dissolved Oxygen
            dissolved_oxygen = (ee.Image(-0.0167).multiply(image.select("B8")).add(ee.Image(0.0067).multiply(image.select("B9"))).add(ee.Image(0.0083).multiply(image.select("B11"))).add(ee.Image(9.577)).rename("Dissolved_Oxygen"))

            # Calculate NDVI
            ndvi = (image.normalizedDifference(["B8", "B4"]).rename("NDVI"))

            # Calculate NDTI
            ndti = (image.normalizedDifference(["B4", "B3"]).rename("NDTI"))

            # Calculate GCI
            gci = (image.select("B3").pow(0.5).multiply(image.select("B4").pow(0.5)).subtract(1).rename("GCI"))

            # Calculate NDCI
            ndci = (image.select("B5").subtract(image.select("B4")).divide(image.select("B5").add(image.select("B4"))).rename("NDCI"))

            # Calculate NDWI
            ndwi = (image.normalizedDifference(["B3", "B8"]).rename("NDWI"))

            # Calculate TSS
            tss = (image.select("B4").subtract(image.select("B8")).pow(2).multiply(0.6113).rename("TSS"))

            # Calculate CDOM
            cdom_index = (image.select("B3").divide(image.select("B2")).rename("CDOM_Index"))

            # Calculate Phycocyanin
            phycocyanin = (ee.Image(26.89).multiply(image.select("B3").divide(image.select("B2"))).subtract(27.43).rename("Phycocyanin"))

            # Calculate Chlorophyll-a
            chl_a = (image.select("B5").add(image.select("B6")).divide(image.select("B4")).rename("Chl-a"))

            # ==================================================
            # 11. EXISTING REDUCE REGION CALCULATIONS
            #
            # Kept unchanged.
            # ==================================================

            ph_mean = (ph.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("pH"))

            dissolved_oxygen_mean = (dissolved_oxygen.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("Dissolved_Oxygen"))

            ndvi_mean = (ndvi.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("NDVI"))

            ndti_mean = (ndti.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("NDTI"))

            gci_mean = (gci.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("GCI"))

            ndci_mean = (ndci.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("NDCI"))

            ndwi_mean = (ndwi.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("NDWI"))

            tss_mean = (tss.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("TSS"))

            cdom_mean = (cdom_index.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("CDOM_Index"))

            phycocyanin_mean = (phycocyanin.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("Phycocyanin"))

            chl_a_mean = (chl_a.reduceRegion(reducer=ee.Reducer.mean(),geometry=geometry,scale=10).get("Chl-a"))

            # ==================================================
            # 12. Get calculated values
            # ==================================================

            data = {"pH": ph_mean.getInfo(),
                    "Dissolved Oxygen":dissolved_oxygen_mean.getInfo(),
                    "NDVI":ndvi_mean.getInfo(),
                    "NDTI":ndti_mean.getInfo(),
                    "GCI":gci_mean.getInfo(),
                    "NDCI":ndci_mean.getInfo(),
                    "NDWI":ndwi_mean.getInfo(),
                    "TSS":tss_mean.getInfo(),
                    "CDOM":cdom_mean.getInfo(),
                    # Existing project behavior:
                    # AQUATIC_MACROPYTES uses NDVI
                    "AQUATIC_MACROPYTES":ndvi_mean.getInfo(),
                    "Phycocyanin":phycocyanin_mean.getInfo(),
                    "Chl-a":chl_a_mean.getInfo(),
            }

            # ==================================================
            # 13. Save parameter data
            #     + Sentinel-2 metadata
            # ==================================================

            parameter = Parameter.objects.create(pond=pond,
                # Existing parameter values
                pH=data.get("pH"),
                dissolved_oxygen=data.get("Dissolved Oxygen"),NDVI=data.get("NDVI"),
                NDTI=data.get("NDTI"),GCI=data.get("GCI"),NDCI=data.get("NDCI"),
                NDWI=data.get("NDWI"),TSS=data.get("TSS"),CDOM=data.get("CDOM"),
                AQUATIC_MACROPYTES=data.get("AQUATIC_MACROPYTES"),Phycocyanin=data.get("Phycocyanin"),Chl_a=data.get("Chl-a"),
                # New Sentinel-2 metadata
                image_id=image_id,image_date=image_date,satellite_name=satellite_name,
                cloud_percentage=cloud_percentage)

            print("\nParameter record saved successfully.")
            print("Parameter ID:",parameter.id)
            print("Processed Image ID:",image_id)

    except Exception as e:

        print("Remote sensing error:",str(e))

        # Re-raise the exception so that the management
        # command knows the processing actually failed.
        raise

    return JsonResponse(
        {
            "message":
                "Remote sensing data processed successfully"
        }
    )