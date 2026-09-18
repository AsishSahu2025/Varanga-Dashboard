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
       