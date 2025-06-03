# MOT Reminder System - Local Installation Guide

## Overview
This guide will help you set up and run the MOT Reminder System locally on your computer. The system allows you to manage vehicle MOT reminders, cross-check vehicle information with the DVLA API, and send automated reminders to customers. It includes advanced OCR capabilities for extracting vehicle registration numbers from images.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)
- Tesseract OCR (required for OCR functionality)
- OpenCV dependencies

## Installation Steps

### 1. Install Tesseract OCR

#### On Windows:
1. Download the installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and follow the instructions
3. Add Tesseract to your PATH or note the installation directory

#### On macOS:
```
brew install tesseract
```

#### On Ubuntu/Debian:
```
sudo apt update
sudo apt install tesseract-ocr
```

### 2. Set Up a Python Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other Python packages.

#### On Windows:
```
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies

With your virtual environment activated, install the required packages:

```
pip install -r requirements.txt
```

### 4. Initialize the Database

The system uses SQLite for local development, which doesn't require additional setup.

Run the application once to create the database:

```
python app.py
```

Then visit `http://127.0.0.1:5000/init-db` in your browser to initialize the database tables.

### 5. Create Upload Directory

Create a directory for OCR image uploads:

```
mkdir -p uploads
```

### 6. Configure Environment Variables (Optional)

Create a `.env` file in the root directory to customize settings:

```
# DVLA API Settings
DVLA_CLIENT_ID=2b3911f4-55f5-4a86-a9f0-0fc02c2bff0f
DVLA_CLIENT_SECRET=rWe8Q~vhlVo7Z_fFuy~zBfAOY5BqCg_PviCwIa74
DVLA_API_KEY=8TfF8vnU2s5sP1CRm7ij69anVlLe5SRm4cNGn9yq

# Email Settings (for actual email sending)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SENDER_EMAIL=garage@example.com

# SMS Settings (for actual SMS sending)
SMS_API_URL=https://api.sms-provider.com
SMS_API_KEY=your_api_key
SMS_SENDER_ID=GarageReminder

# OCR Settings (if Tesseract is not in PATH)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Running the Application

1. Ensure your virtual environment is activated
2. Start the application:

```
python app.py
```

3. Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

## Using the OCR Feature

The MOT Reminder System includes advanced OCR capabilities for extracting vehicle registration numbers from images:

### Uploading Images for OCR

1. Navigate to the Vehicles page
2. Click the "Add Vehicle" button
3. In the vehicle form, click the "Upload Image" button
4. Select an image containing a vehicle registration plate
5. The system will process the image and extract potential registration numbers
6. If multiple registrations are found, you can select the correct one
7. If the OCR is incorrect, you can manually edit the registration
8. Click "Lookup" to verify the registration with the DVLA API
9. Complete the vehicle form and save

### OCR Tips for Best Results

- Ensure the registration plate is clearly visible in the image
- Good lighting and contrast will improve OCR accuracy
- Avoid extreme angles or distorted images
- If OCR fails, try cropping the image to focus on the registration plate
- The system can handle common OCR errors (e.g., 0/O, 1/I, 5/S confusion)
- Always verify the extracted registration before saving

## Using the System

### Dashboard
The dashboard provides an overview of:
- Total vehicles in the system
- Total customers
- Reminders due now
- Options to process reminders or schedule new ones

### Managing Vehicles
- Add vehicles manually or look them up via the DVLA API
- Upload images to extract registration numbers using OCR
- Edit vehicle details
- Cross-check vehicle information with DVLA records
- Delete vehicles when needed

### Managing Customers
- Add and edit customer information
- View vehicles associated with each customer
- Delete customers (only if they have no associated vehicles)

### Managing Reminders
- Schedule reminders manually
- Use the "Schedule Reminders" feature to automatically create reminders based on MOT expiry dates
- Process reminders to send notifications (simulated in local mode)
- View reminder history and status

### Settings
- Configure email and SMS settings
- Customize reminder templates
- Set up DVLA API credentials

## DVLA API Integration

In local development mode, the system uses mock data to simulate DVLA API responses. In a production environment, you would need to replace the mock implementation in `services/dvla_api_service.py` with actual API calls using your credentials.

## Email and SMS Notifications

In local development mode, email and SMS sending is simulated (logged to console). To enable actual sending:

1. Configure the appropriate settings in your `.env` file
2. Modify the `services/reminder_service.py` file to uncomment the actual sending code and comment out the simulation code

## Troubleshooting

### OCR Issues
If you encounter problems with OCR:
1. Verify Tesseract is correctly installed and accessible
2. For Windows users, set the `TESSERACT_CMD` environment variable to your Tesseract executable path
3. Try different image formats or improve image quality
4. Check the console for specific error messages

### Database Issues
If you encounter database errors, you can reset the database by:
1. Stopping the application
2. Deleting the `mot_reminder.db` file
3. Restarting the application
4. Visiting `http://127.0.0.1:5000/init-db` to reinitialize the database

### API Connection Issues
If you're implementing actual DVLA API calls and encounter connection issues:
1. Verify your API credentials in the `.env` file
2. Check your internet connection
3. Ensure the API endpoints are correct in `services/dvla_api_service.py`

## Support and Further Development

This system is designed for local use and can be extended as needed. Some potential enhancements include:

- User authentication and multi-user support
- Integration with garage management systems
- Advanced reporting and analytics
- Mobile app notifications
- Appointment scheduling integration

For any questions or issues, please refer to the code documentation or contact the developer.
