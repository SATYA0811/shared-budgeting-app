# Shared Budgeting Application 🇨🇦

A comprehensive full-stack budgeting application designed for Canadian banking with transaction tracking, categorization, analytics, and goal management.

## 🚧 Development Status

**This project is currently in active development (Alpha phase)**

- ✅ Core backend functionality implemented
- ✅ Multi-page frontend with React
- ✅ User authentication and data isolation  
- ✅ Transaction management and analytics
- ✅ **Canadian banking integration (CIBC, RBC, TD, BMO, AMEX)**
- ✅ **PDF/CSV bank statement parsing**
- ✅ **CAD currency formatting and Canadian date formats**
- 🚧 Mobile responsiveness in progress
- 🚧 Advanced analytics features being added
- 📋 See [CHANGELOG.md](CHANGELOG.md) for detailed version history and upcoming features

## 🌟 Features

### ✅ Authentication & Security
- User registration and login with JWT tokens
- Secure password hashing with bcrypt
- Rate limiting on sensitive endpoints
- CORS and security headers
- Input validation and sanitization

### ✅ Transaction Management 🏦
- Manual transaction entry and editing
- **Canadian bank statement parsing** (CIBC, RBC, TD, BMO, Scotiabank, AMEX)
- File upload for bank statements (PDF, CSV, Excel)
- **Enhanced parsing for Canadian date formats** (DD/MM/YYYY, YYYY/MM/DD)
- Automatic transaction categorization with rules
- Category management with budgets
- **CAD currency formatting** with Canadian locale support

### ✅ Analytics & Insights
- Spending trends and patterns over time
- Category-wise spending analysis
- Budget vs actual performance tracking
- Monthly financial reports
- Personalized insights and recommendations

### ✅ Goals & Savings
- Goal creation with target amounts and dates
- Progress tracking and visualization
- Contribution logging
- Achievement notifications

### ✅ Production Ready
- Database indexes for optimal performance
- Comprehensive error handling and logging
- Health checks and monitoring endpoints
- Docker containerization
- Environment-based configuration

## 🏦 Canadian Banking Support

This application is specifically designed for Canadian banking with comprehensive support for major Canadian financial institutions:

### 🇨🇦 Supported Banks
- **CIBC** (Canadian Imperial Bank of Commerce)
- **RBC** (Royal Bank of Canada)  
- **TD Canada Trust**
- **BMO** (Bank of Montreal)
- **Scotiabank**
- **American Express Canada**
- **Tangerine**

### 📄 Statement Parsing
- **PDF Bank Statements** - Automatic text and table extraction
- **CSV Exports** - Enhanced column detection for Canadian bank formats
- **Auto-Detection** - Automatically identifies bank type and applies appropriate parsing rules
- **Date Format Support** - Handles DD/MM/YYYY, YYYY/MM/DD, and other Canadian date formats

### 💰 Currency & Formatting
- **CAD Currency Display** - All amounts shown as `$1,234.56 CAD`
- **Canadian Locale** - Number formatting follows Canadian standards
- **Date Formatting** - Uses Canadian date format preferences

### 🔧 File Upload Features
- **Drag & Drop** - Easy file upload interface
- **Multiple Formats** - Supports PDF, CSV, and Excel files
- **Working Upload Buttons** - Fixed upload functionality in both Transactions and Banks pages
- **Real-time Processing** - Immediate transaction parsing and import

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shared-budgeting-app
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Frontend Setup** (if available)
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

### Using Docker

1. **Development with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Production Deployment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///./budgeting.db
# or for production:
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-very-secure-secret-key-here-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# URLs
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Production Deployment

For production deployment, ensure:
1. Change `SECRET_KEY` to a secure random value
2. Use PostgreSQL instead of SQLite
3. Set `ENVIRONMENT=production`
4. Configure proper CORS origins
5. Set up proper SSL/TLS certificates

## 📊 API Endpoints

### Authentication
- `POST /register` - Register new user (Rate limited: 5/minute)
- `POST /login` - Login user (Rate limited: 10/minute)
- `GET /me` - Get current user info

### Transactions
- `GET /transactions` - List transactions with filtering
- `POST /transactions` - Create new transaction
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

### Categories
- `GET /categories` - List all categories
- `POST /categories` - Create new category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Goals
- `GET /goals` - List user goals
- `POST /goals` - Create new goal
- `PUT /goals/{id}` - Update goal
- `DELETE /goals/{id}` - Delete goal
- `POST /goals/{id}/contribute` - Add contribution to goal

### Analytics
- `GET /analytics/spending-trends` - Monthly spending trends
- `GET /analytics/category-analysis` - Category-wise analysis
- `GET /analytics/monthly-report/{year}/{month}` - Monthly report
- `GET /analytics/budget-performance` - Budget vs actual
- `GET /analytics/insights` - Personalized insights

### File Upload 🇨🇦
- `POST /upload-statement` - Upload bank statement (Rate limited: 20/hour)
  - **Supports Canadian banks**: CIBC, RBC, TD Canada Trust, BMO, Scotiabank, AMEX Canada
  - **Auto-detects bank format** and applies specialized parsing
  - **PDF parsing** with table extraction for bank statements  
  - **CSV parsing** with Canadian date format support (DD/MM/YYYY, YYYY/MM/DD)
  - **Enhanced column detection** for Canadian bank CSV exports

### Health & Monitoring
- `GET /health` - Health check endpoint
- `GET /debug` - Debug info (development only)

## 🛡️ Security Features

1. **Rate Limiting**
   - Registration: 5 requests per minute
   - Login: 10 requests per minute  
   - File upload: 20 requests per hour

2. **Authentication**
   - JWT tokens with configurable expiration
   - Secure password hashing with bcrypt
   - User-based data isolation

3. **Input Validation**
   - Pydantic models for request/response validation
   - File type and size restrictions
   - SQL injection protection via SQLAlchemy ORM

4. **Security Headers**
   - CORS configuration
   - Trusted host middleware
   - Comprehensive error handling

## 📈 Performance Optimizations

1. **Database Indexes**
   - Optimized queries for transactions by user_id, date, category
   - Composite indexes for common query patterns
   - Indexed foreign key relationships

2. **Caching** (Production)
   - Redis integration for session storage
   - Rate limiting storage in Redis

3. **Monitoring**
   - Request logging with execution time
   - Health check endpoints
   - Error tracking and logging

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Ensure database is initialized
   python -c "from app.database import create_tables; create_tables()"
   ```

2. **JWT Token Issues**
   ```bash
   # Check if SECRET_KEY is properly set
   curl -X GET "http://localhost:8000/debug-auth" -H "Authorization: Bearer <token>"
   ```

3. **File Upload Issues**
   ```bash
   # Check upload directory exists and has proper permissions
   mkdir -p uploads
   chmod 755 uploads
   ```

## 📝 Development

### Project Structure
```
shared-budgeting-app/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── auth.py          # Authentication logic
│   │   ├── database.py      # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── config.py        # Application settings
│   │   ├── parsers/         # Canadian bank parsers 🇨🇦
│   │   │   ├── __init__.py
│   │   │   └── canadian_banks.py  # CIBC, RBC, TD, AMEX parsers
│   │   └── routers/         # API route handlers
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Docker configuration
├── frontend/               # React frontend 🇨🇦
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Application pages
│   │   └── services/       # API integration
│   └── package.json
├── docker-compose.yml      # Development compose
├── docker-compose.prod.yml # Production compose
└── .env.example           # Environment template
```

### Testing

Run the application and test endpoints:
```bash
# Test health check
curl http://localhost:8000/health

# Register a user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Test Canadian bank file upload
curl -X POST "http://localhost:8000/upload-statement" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@path/to/cibc_statement.pdf"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Latest Release: v0.4.0 (2025-08-13) 🇨🇦
- **Canadian Banking Integration** - Full support for CIBC, RBC, TD, BMO, Scotiabank, AMEX
- **Enhanced File Upload** - Working PDF and CSV parsing with Canadian bank formats  
- **CAD Currency Support** - Proper Canadian dollar formatting and locale support
- **Canadian Date Formats** - Support for DD/MM/YYYY and YYYY/MM/DD formats
- **Specialized Bank Parsers** - Auto-detection and parsing for major Canadian banks
- **Fixed Upload Functionality** - Resolved file upload issues in frontend
- Multi-page frontend with React Router
- Enhanced user data isolation
- Comprehensive analytics and goals tracking

### Current Development Phase: Alpha
- Core functionality implemented and tested
- User interface and API integration complete
- Active bug fixes and feature enhancements
- Performance optimizations ongoing

---

For support or questions, please open an issue on GitHub.