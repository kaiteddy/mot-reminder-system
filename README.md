# 🚗 MOT Reminder System

A comprehensive garage management system for tracking MOT reminders, customer data, and vehicle information with DVLA integration.

## ✨ Features

### 🎯 Core Functionality
- **MOT Reminder Management** - Automated tracking of MOT expiry dates
- **DVLA Integration** - Real-time vehicle data from DVLA MOT History API
- **Customer Management** - Comprehensive customer database with contact details
- **Multi-file Upload** - Support for CSV and XLSX files
- **Smart Data Processing** - Automatic customer parsing and vehicle matching

### 📊 Data Management
- **GA4 Job Sheets Import** - Import garage management data
- **Vehicle Database** - Complete vehicle information with VIN, make, model
- **Customer Parsing** - Extract names, phone numbers, and emails from combined fields
- **MOT History** - Full MOT test history from DVLA
- **Reminder Scheduling** - Automated reminder generation and tracking

### 🎨 User Interface
- **Modern Dashboard** - Clean, professional interface
- **Light/Dark Themes** - User-selectable theme with toggle
- **Responsive Design** - Works on desktop and mobile devices
- **UK Number Plates** - Authentic yellow number plate styling
- **Interactive Tables** - Clickable rows with detailed modals
- **Real-time Search** - Filter and search functionality

### 🔗 Integrations
- **DVLA MOT Check** - Direct links to official DVLA MOT checker
- **MOT History API** - Real-time MOT data retrieval
- **Excel/CSV Support** - Import from various file formats
- **Database Management** - SQLite with automatic migrations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaiteddy/mot-reminder-system.git
   cd mot-reminder-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your DVLA API credentials
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

## 📁 Project Structure

```
mot-reminder-system/
├── app.py                 # Main Flask application
├── database.py           # Database configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── models/              # Database models
│   ├── customer.py
│   ├── vehicle.py
│   ├── reminder.py
│   └── job_sheet.py
├── routes/              # Application routes
│   ├── main.py
│   ├── upload.py
│   ├── reminders.py
│   └── api.py
├── services/            # Business logic
│   ├── dvla_service.py
│   ├── customer_parser.py
│   └── reminder_service.py
├── static/              # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # HTML templates
└── uploads/            # File upload directory
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# DVLA API Configuration
DVLA_API_KEY=your_dvla_api_key_here
DVLA_API_URL=https://beta.check-mot.service.gov.uk/trade/vehicles/mot-tests

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///mot_reminder.db
```

### DVLA API Setup

1. Register for DVLA MOT History API access
2. Obtain your API key
3. Add the key to your `.env` file

## 📊 Usage

### 1. Upload Data
- Navigate to **Upload** section
- Select CSV or XLSX files
- Support for GA4 job sheets and customer data
- Automatic data processing and validation

### 2. Manage Reminders
- View all MOT reminders in the **Reminders** section
- Filter by urgency, status, or date range
- Click on any row for detailed vehicle information
- Generate new reminders automatically

### 3. Customer Management
- Access customer data through the **Customer Hub**
- View customer details, vehicles, and MOT history
- Edit customer information and contact details

### 4. Vehicle Details
- Click on any vehicle registration for full details
- View DVLA-sourced vehicle information
- See complete MOT test history
- Direct links to official DVLA MOT checker

## 🎨 Themes

The application supports both light and dark themes:

- **Dark Theme** (default) - Professional dark interface
- **Light Theme** - Clean light interface for better visibility
- **Theme Toggle** - Fixed toggle button in top-right corner

## 📱 Responsive Design

- **Desktop** - Full-featured interface with all functionality
- **Tablet** - Optimized layout for medium screens
- **Mobile** - Compact interface with essential features

## 🔒 Security Features

- Environment variable configuration
- Secure file upload handling
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Database Management

```bash
# Reset database
python database.py

# Regenerate reminders
python regenerate_reminders.py
```

### Testing

```bash
# Test customer parser
python test_customer_parser.py

# Test DVLA integration
python fix_dvla_data.py
```

## 📝 Data Formats

### GA4 Job Sheets CSV Format
```csv
ID,Doc Type,Doc No,Date,Customer,Vehicle,Registration,VIN,Mileage,Labour,Parts,MOT,VAT
```

### Customer Data Format
Customer field format: `Name t: landline m: mobile e: email`

### MOT Data CSV Format
```csv
Registration,Customer,MOT_Expiry,Reminder_Date,Status
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [Installation Guide](INSTALLATION_GUIDE.md)
- Review the documentation

## 🙏 Acknowledgments

- DVLA for providing the MOT History API
- Flask community for the excellent framework
- Bootstrap for the responsive UI components

---

**Built with ❤️ for garage management and MOT tracking**
