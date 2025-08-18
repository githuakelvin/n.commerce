# 🇰🇪 Kenya Commerce - E-Commerce Platform

A fully functional, modern e-commerce website built specifically for the Kenyan market with M-Pesa integration, local payment methods, and comprehensive product management.

## 🚀 Features

### 🛍️ **E-Commerce Core**
- **Product Management**: Add, edit, and manage products with categories, brands, and specifications
- **Inventory Control**: Track stock levels, low stock alerts, and automated inventory management
- **Shopping Cart**: Persistent cart with session and user-based storage
- **Wishlist**: Save favorite products for later purchase
- **Order Management**: Complete order lifecycle from cart to delivery

### 💳 **Payment Integration**
- **M-Pesa Integration**: Native M-Pesa STK Push and Paybill integration
- **Card Payments**: Stripe, Flutterwave, and Pesapal support
- **Cash on Delivery**: COD option for local customers
- **Bank Transfer**: Direct bank payment support
- **Multiple Currencies**: KES (Kenyan Shilling) primary, with multi-currency support

### 🚚 **Delivery & Logistics**
- **County-based Shipping**: Shipping rates based on Kenyan counties
- **Pickup Points**: Multiple pickup locations in major cities
- **Real-time Tracking**: Order status updates and delivery tracking
- **SMS Notifications**: Automated delivery updates via SMS

### 👥 **User Management**
- **Customer Accounts**: User registration, profiles, and order history
- **Admin Dashboard**: Comprehensive admin interface for business owners
- **Role-based Access**: Different permission levels for staff and administrators
- **Address Management**: Multiple delivery addresses per user

### 📱 **Mobile-First Design**
- **Responsive Design**: Optimized for all devices and screen sizes
- **Progressive Web App**: PWA features for mobile users
- **WhatsApp Integration**: Direct customer support via WhatsApp
- **Mobile Payments**: Optimized for mobile payment methods

### 🔍 **Search & Discovery**
- **Advanced Search**: Product search with filters and sorting
- **Category Navigation**: Organized product categories and subcategories
- **Product Reviews**: Customer ratings and review system
- **Recommendations**: AI-powered product suggestions

### 📊 **Marketing & SEO**
- **Newsletter System**: Email marketing and promotional campaigns
- **Social Media Integration**: Facebook, Instagram, and WhatsApp links
- **SEO Optimization**: Meta tags, structured data, and search engine optimization
- **Blog System**: Content marketing and SEO content management

### 🛡️ **Security & Compliance**
- **SSL Certificate**: Secure HTTPS connections
- **GDPR Compliance**: Data protection and privacy compliance
- **Secure Payments**: PCI DSS compliant payment processing
- **User Privacy**: Comprehensive privacy controls and data management

## 🛠️ Technology Stack

### **Backend**
- **Django 4.2.7**: Python web framework
- **Django REST Framework**: API development
- **SQLite/PostgreSQL**: Database (easily migratable)
- **Celery**: Background task processing
- **Redis**: Caching and session storage

### **Frontend**
- **HTML5/CSS3**: Modern, semantic markup
- **Bootstrap 5.3**: Responsive CSS framework
- **JavaScript/jQuery**: Interactive functionality
- **Font Awesome**: Icon library
- **Responsive Design**: Mobile-first approach

### **Payment Gateways**
- **M-Pesa API**: Native Kenyan mobile money
- **Stripe**: International card payments
- **Flutterwave**: African payment gateway
- **Pesapal**: East African payments

### **Deployment & Hosting**
- **Gunicorn**: WSGI server
- **Whitenoise**: Static file serving
- **Docker**: Containerization support
- **Nginx**: Web server (production)

## 📋 Requirements

### **System Requirements**
- Python 3.8+
- Node.js 14+ (for frontend assets)
- PostgreSQL 12+ (production)
- Redis 6+ (for caching)

### **Python Dependencies**
- Django 4.2.7
- Django REST Framework 3.14.0
- Pillow 10.1.0 (image processing)
- Celery 5.3.4 (background tasks)
- Redis 5.0.1 (caching)

## 🚀 Quick Start

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/kenya-commerce.git
cd kenya-commerce
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Configuration**
Create a `.env` file in the project root:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway Settings
STRIPE_PUBLISHABLE_KEY=your-stripe-key
STRIPE_SECRET_KEY=your-stripe-secret

# M-Pesa Settings
MPESA_CONSUMER_KEY=your-mpesa-key
MPESA_CONSUMER_SECRET=your-mpesa-secret
MPESA_PASSKEY=your-mpesa-passkey
MPESA_SHORTCODE=your-mpesa-shortcode
MPESA_ENVIRONMENT=sandbox

# WhatsApp API
WHATSAPP_API_KEY=your-whatsapp-key
WHATSAPP_PHONE_NUMBER=254700000000
```

### **5. Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **6. Create Superuser**
```bash
python manage.py createsuperuser
```

### **7. Collect Static Files**
```bash
python manage.py collectstatic
```

### **8. Run Development Server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view your e-commerce website!

## 🗄️ Database Models

### **Core Models**
- **User Management**: CustomUser, UserProfile, Address
- **Products**: Product, Category, Brand, ProductImage, ProductReview
- **Orders**: Order, OrderItem, OrderStatus
- **Payments**: Payment, MpesaPayment, CardPayment, Refund
- **Delivery**: ShippingZone, PickupPoint
- **Marketing**: Newsletter, Coupon, SocialMedia

### **Key Features**
- **Product Variants**: Color, size, and other attributes
- **Inventory Tracking**: Real-time stock management
- **Order Processing**: Complete order workflow
- **Payment Processing**: Multiple payment method support
- **Customer Management**: Comprehensive user profiles

## 🔧 Configuration

### **Payment Gateway Setup**

#### **M-Pesa Configuration**
1. Register for M-Pesa API access
2. Configure business shortcode and passkey
3. Set up webhook endpoints
4. Test with sandbox environment

#### **Stripe Configuration**
1. Create Stripe account
2. Get API keys from dashboard
3. Configure webhook endpoints
4. Set up payment methods

### **Email Configuration**
1. Configure SMTP settings
2. Set up email templates
3. Test email delivery
4. Configure newsletter system

### **SMS Configuration**
1. Set up SMS gateway (Twilio, Africa's Talking)
2. Configure delivery notifications
3. Test SMS delivery

## 📱 Mobile Optimization

### **Responsive Design**
- Mobile-first approach
- Touch-friendly interfaces
- Optimized for small screens
- Fast loading on mobile networks

### **PWA Features**
- Offline functionality
- App-like experience
- Push notifications
- Home screen installation

## 🚀 Deployment

### **Production Deployment**

#### **1. Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server -y
```

#### **2. Application Deployment**
```bash
# Clone repository
git clone https://github.com/yourusername/kenya-commerce.git
cd kenya-commerce

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

#### **3. Gunicorn Configuration**
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/kenya-commerce.service
```

Service file content:
```ini
[Unit]
Description=Kenya Commerce Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/kenya-commerce
ExecStart=/path/to/kenya-commerce/venv/bin/gunicorn --workers 3 --bind unix:/path/to/kenya-commerce/kenya-commerce.sock kenya_commerce.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

#### **4. Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/kenya-commerce
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/kenya-commerce;
    }

    location /media/ {
        root /path/to/kenya-commerce;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/kenya-commerce/kenya-commerce.sock;
    }
}
```

#### **5. SSL Certificate**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t kenya-commerce .
docker run -p 8000:8000 kenya-commerce
```

## 🔒 Security Features

### **Data Protection**
- **Encryption**: All sensitive data encrypted at rest
- **HTTPS**: Secure connections with SSL/TLS
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Prevention**: Input sanitization and output encoding

### **Payment Security**
- **PCI Compliance**: Payment card industry standards
- **Tokenization**: Secure payment token storage
- **Fraud Detection**: Basic fraud prevention measures
- **Audit Logging**: Complete payment transaction logs

### **User Privacy**
- **GDPR Compliance**: European data protection standards
- **Data Minimization**: Collect only necessary data
- **User Consent**: Explicit consent for data processing
- **Data Portability**: User data export functionality

## 📊 Performance Optimization

### **Caching Strategy**
- **Redis Caching**: Session and data caching
- **Database Optimization**: Query optimization and indexing
- **CDN Integration**: Content delivery network support
- **Image Optimization**: Compressed and optimized images

### **Database Optimization**
- **Indexing**: Strategic database indexes
- **Query Optimization**: Efficient database queries
- **Connection Pooling**: Database connection management
- **Read Replicas**: Database scaling for high traffic

## 🧪 Testing

### **Test Coverage**
```bash
# Run tests
python manage.py test

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

### **Test Types**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete user workflow testing
- **Performance Tests**: Load and stress testing

## 📈 Monitoring & Analytics

### **Application Monitoring**
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Monitoring**: Application performance metrics
- **User Analytics**: User behavior and conversion tracking
- **Server Monitoring**: Server health and resource usage

### **Business Intelligence**
- **Sales Analytics**: Revenue and order analytics
- **Customer Insights**: Customer behavior analysis
- **Inventory Reports**: Stock level and turnover reports
- **Marketing ROI**: Campaign performance tracking

## 🔄 Updates & Maintenance

### **Regular Updates**
- **Security Patches**: Monthly security updates
- **Feature Updates**: Quarterly feature releases
- **Bug Fixes**: Continuous bug fix deployment
- **Performance Improvements**: Ongoing optimization

### **Backup Strategy**
- **Database Backups**: Daily automated backups
- **File Backups**: Media and static file backups
- **Configuration Backups**: Environment and settings backup
- **Disaster Recovery**: Complete system recovery plan

## 🌍 Localization

### **Language Support**
- **English**: Primary language
- **Swahili**: Local language support
- **Multi-language**: Easy addition of more languages
- **RTL Support**: Right-to-left language support

### **Currency Support**
- **KES**: Kenyan Shilling (primary)
- **USD**: US Dollar support
- **EUR**: Euro support
- **Multi-currency**: Easy currency addition

## 📞 Support & Documentation

### **Documentation**
- **API Documentation**: Complete API reference
- **User Guides**: Customer and admin guides
- **Developer Docs**: Technical implementation details
- **Video Tutorials**: Step-by-step setup guides

### **Support Channels**
- **Email Support**: support@kenyacommerce.co.ke
- **WhatsApp Support**: +254 700 000 000
- **Phone Support**: +254 700 000 000
- **Live Chat**: In-app chat support

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### **Code Standards**
- **PEP 8**: Python code style guide
- **ESLint**: JavaScript code quality
- **Prettier**: Code formatting
- **Type Hints**: Python type annotations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Community**: For the excellent web framework
- **Bootstrap Team**: For the responsive CSS framework
- **Font Awesome**: For the icon library
- **Kenyan Developers**: For local market insights

## 📞 Contact

- **Website**: [https://kenyacommerce.co.ke](https://kenyacommerce.co.ke)
- **Email**: info@kenyacommerce.co.ke
- **Phone**: +254 700 000 000
- **WhatsApp**: +254 700 000 000

---

**🇰🇪 Built with ❤️ for the Kenyan market**

*Empowering Kenyan businesses with world-class e-commerce solutions*




