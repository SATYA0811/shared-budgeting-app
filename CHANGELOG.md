# Changelog

All notable changes to the Shared Budgeting App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-08-13 🇨🇦

### 🏦 Canadian Banking Integration
- **Major Canadian Banks Support**: Full integration for CIBC, RBC, TD Canada Trust, BMO, Scotiabank, American Express Canada, and Tangerine
- **Specialized Bank Parsers**: New `/app/parsers/canadian_banks.py` module with bank-specific parsing logic
  - Auto-detection of bank type from PDF/CSV content
  - CIBC format: Date | Description | Debit | Credit | Balance
  - RBC format: Date | Description | Withdrawals | Deposits | Balance  
  - AMEX Canada format: Date | Description | Amount
  - TD format: Date | Description | Debit | Credit | Balance
- **Enhanced Date Format Support**: DD/MM/YYYY, YYYY/MM/DD, and other Canadian date formats
- **Canadian CSV Column Detection**: Enhanced parsing for Canadian bank CSV exports with columns like "Posting Date", "Transaction Details", "CAD$"

### 💰 CAD Currency & Localization
- **Canadian Dollar Formatting**: All amounts display as `$1,234.56 CAD` using Canadian locale (en-CA)
- **Date Localization**: Canadian date format preferences (YYYY-MM-DD display)
- **Bank Account Display**: Updated to show Canadian banks with CAD currency indicators
- **Transaction Display**: Enhanced formatting with Canadian locale for numbers and dates

### 🔧 Fixed File Upload Functionality
- **Frontend Upload Integration**: Resolved file upload issues across the application
  - Fixed Import button in Transactions page - now opens FileUpload modal
  - Fixed Upload Center in Banks page - working drag-drop and button uploads
  - Connected FileUpload component properly to both pages
  - Added success callbacks to reload data after upload
- **Backend API Connectivity**: Fixed communication between frontend and backend
  - Updated frontend API URL from port 8000 to 8001
  - Resolved CORS issues
  - Enhanced error handling in upload process

### 🎨 Enhanced User Interface
- **Canadian Banking Theme**: Updated UI to reflect Canadian banking context
  - Bank account cards show CIBC, RBC, TD Canada Trust, BMO instead of US banks
  - Integration status updated for Canadian financial institutions
  - File upload instructions mention Canadian bank compatibility
- **Upload Experience**: Improved file upload interface
  - Multiple upload entry points (Transactions page, Banks page Upload Center)
  - Enhanced drag-and-drop functionality
  - Better error messages and success feedback
  - Real-time processing indicators

### 🧪 Testing & Validation
- **Verified Canadian Bank Parsing**: Successfully tested with Canadian transaction data
  - Tested CSV upload with DD/MM/YYYY dates and CAD amounts
  - Verified proper transaction extraction and formatting
  - Confirmed Canadian locale formatting in UI
- **Upload Functionality**: End-to-end testing of file upload system
  - PDF parsing with Canadian bank statements
  - CSV parsing with Canadian bank formats
  - API integration and data persistence

### 📚 Documentation Updates
- **README Enhancement**: Comprehensive documentation of Canadian banking features
  - New "Canadian Banking Support" section
  - Detailed supported banks list
  - Currency and formatting explanations
  - File upload feature descriptions
- **Version Updates**: Bumped all components to v0.4.0
  - Frontend package.json
  - Backend FastAPI application
  - Health check endpoint

## [0.3.0] - 2025-08-11

### 🎯 Major Features
- **Multi-Page Frontend**: Complete React application with 6 main sections
  - Dashboard/Summary with financial overview
  - Transactions management with filtering and bulk operations
  - Analytics with spending trends and budget performance
  - Goals tracking with progress monitoring
  - Banks integration and file upload
  - Partners/Household collaboration features

### 🔧 Backend Enhancements
- **Enhanced Database Models**: Added comprehensive relationships and new tables
  - BankAccount model with Plaid integration support
  - GoalContribution tracking with analytics
  - SharedExpense and SharedExpenseSplit for household collaboration
  - Enhanced Transaction model with recurring support
- **New API Routers**: 
  - Banks router for account management and file processing
  - Partners router for household collaboration
  - Enhanced Goals router with category and priority support
  - Improved Analytics with user-specific insights

### 🐛 Bug Fixes
- **User Data Isolation**: Fixed new users seeing predefined data
  - Analytics now only shows categories where users have transactions
  - Banks integration status hidden for new users until first account
  - Proper user filtering across all endpoints
- **API Route Ordering**: Fixed FastAPI route conflicts
  - Moved `/summary` and `/statistics` routes before `/{id}` patterns
  - Resolved 404 errors for dashboard endpoints

### 🎨 Frontend Improvements
- **React Router**: Full navigation between pages
- **Enhanced UI Components**: TailwindCSS with custom utility classes
- **Data Visualization**: Charts and analytics with Recharts
- **Form Handling**: Comprehensive forms for transactions, goals, and settings
- **Authentication Flow**: Complete login/register system integration

### 🔒 Security & Authentication
- **JWT Token Management**: Proper authentication flow
- **User Session Handling**: Automatic logout on token expiration
- **Protected Routes**: All API endpoints properly secured
- **Input Validation**: Enhanced validation across all forms

### 📱 User Experience
- **Clean New User Experience**: Empty dashboards instead of sample data
- **Progressive Data Loading**: Users see their own data as they add it
- **Error Handling**: Better error messages and user feedback
- **Loading States**: Proper loading indicators throughout the app

## [0.2.0] - 2025-08-10

### Added
- **Authentication System**: User registration and login with JWT tokens
- **File Upload**: Bank statement processing (PDF, CSV, Excel support)
- **Transaction Categorization**: Manual and rule-based categorization
- **Enhanced Database Schema**: Improved models with relationships
- **API Documentation**: Comprehensive OpenAPI/Swagger documentation

### Improved
- **Database Performance**: Added indexes for better query performance
- **Error Handling**: Enhanced error messages and validation
- **Code Organization**: Modular router structure

## [0.1.0] - 2025-08-09

### Added
- **Initial Project Setup**: FastAPI backend with SQLite database
- **Basic Models**: User, Transaction, Category, Income, Goal models
- **REST API Foundation**: Basic CRUD operations
- **Frontend Structure**: Initial React setup with Vite
- **Development Environment**: Docker and local development configuration

### Infrastructure
- **Database**: SQLite with SQLAlchemy ORM
- **Backend**: FastAPI with async support
- **Frontend**: React with modern JavaScript
- **Styling**: TailwindCSS integration
- **Build Tools**: Vite for fast development

---

## Development Status

🚧 **This project is currently in active development** 🚧

### Current Phase: Alpha
- Core functionality implemented
- User interface and API mostly complete
- Testing and refinement ongoing

### Upcoming Features
- [ ] Plaid bank integration
- [ ] Mobile responsive design
- [ ] Advanced analytics and reporting
- [ ] Budget forecasting
- [ ] Export functionality (PDF reports)
- [ ] Email notifications
- [ ] Multi-currency support
- [ ] Investment tracking
- [ ] Bill reminders

### Known Issues
- Some edge cases in file upload processing
- Mobile responsiveness needs improvement
- Advanced analytics features in development
- Performance optimization needed for large datasets

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner  
- **PATCH** version for backwards compatible bug fixes

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.