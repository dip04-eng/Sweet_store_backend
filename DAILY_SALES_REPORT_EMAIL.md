# Daily Sales Report Email Feature

## Overview
The system now automatically sends a daily sales report email to the manager containing all orders scheduled for the next day. This helps the manager plan and prepare for upcoming deliveries.

## Features

### 🚀 **Automatic Daily Email**
- **Scheduled Time**: 6:00 PM IST (Indian Standard Time) by default
- **Report Content**: All orders with delivery date = next day
- **Email Includes**:
  - Total number of orders
  - Total revenue
  - Total paid amount
  - Total due amount
  - Detailed PDF attachment with all order information
  - List of items to prepare

### 📧 **Email Configuration**
Configuration is stored in `.env` file:

```env
# Email Configuration
OUTLOOK_EMAIL=your-email@outlook.com
OUTLOOK_PASSWORD=your-password
OUTLOOK_HOST=smtp.office365.com
OUTLOOK_PORT=587
MANAGER_EMAIL=manager@email.com

# Daily Sales Report Configuration (Time in IST)
DAILY_REPORT_HOUR=18
DAILY_REPORT_MINUTE=0
```

## How It Works

### 1. **Scheduled Task**
- Uses APScheduler to run daily at configured time
- Timezone: Asia/Kolkata (IST)
- Automatically starts when Flask server starts
- Runs in background without blocking the server

### 2. **Report Generation Process**
```
1. Calculate tomorrow's date
2. Query database for orders with deliveryDate = tomorrow
3. Generate sales summary (revenue, paid, due, items)
4. Create PDF report with all details
5. Send email to manager with PDF attachment
6. Log success/failure
```

### 3. **Email Content**
The email includes:
- **Header**: Mansoor Hotel & Sweets branding
- **Summary Section**: 
  - Total orders count
  - Total revenue (₹)
  - Total paid (₹)
  - Total due (₹)
- **Attached PDF**: Complete order details with customer information
- **Action Items**: Checklist for manager to prepare for next day

## Testing the Feature

### **Test Endpoint Available**
You can manually trigger the email for testing:

**Endpoint**: `POST /admin/test_sales_report_email`

**Request Body** (optional):
```json
{
  "date": "2026-01-29"
}
```

If no date is provided, it defaults to tomorrow's date.

**Example using PowerShell**:
```powershell
$body = @{
    date = "2026-01-29"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/admin/test_sales_report_email" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Example using curl**:
```bash
curl -X POST http://127.0.0.1:5000/admin/test_sales_report_email \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-01-29"}'
```

## Configuration Options

### **Change Email Time**
Edit `.env` file to change the scheduled time:

```env
# Send report at 8:00 PM instead of 6:00 PM
DAILY_REPORT_HOUR=20
DAILY_REPORT_MINUTE=0

# Send report at 5:30 PM
DAILY_REPORT_HOUR=17
DAILY_REPORT_MINUTE=30
```

### **Change Manager Email**
```env
MANAGER_EMAIL=new-manager@email.com
```

### **Use Different SMTP Provider**
```env
# For Gmail
OUTLOOK_HOST=smtp.gmail.com
OUTLOOK_PORT=587
OUTLOOK_EMAIL=your-email@gmail.com
OUTLOOK_PASSWORD=your-app-password

# For other providers, check their SMTP settings
```

## Server Logs

When the server starts, you'll see:
```
============================================================
⏰ Scheduled Task Configured
============================================================
📧 Daily sales report will be sent at 18:00 IST
📨 Report will be sent to: manager@email.com
============================================================
```

When the scheduled task runs:
```
============================================================
📧 SCHEDULED TASK: Sending Daily Sales Report
============================================================
📅 Generating report for: 2026-01-29
📊 Found 5 order(s) for 2026-01-29
💰 Total Revenue: ₹15000
✅ Sales report email sent successfully to manager!
============================================================
```

## Troubleshooting

### **Email Not Sending**
1. Check `.env` file has correct email credentials
2. Verify MANAGER_EMAIL is set
3. Check server logs for error messages
4. Test using the test endpoint
5. Ensure SMTP credentials are valid (try logging into email manually)

### **Wrong Time Zone**
The scheduler uses IST (Indian Standard Time). If you need a different timezone:
1. Edit `app.py`
2. Change `pytz.timezone('Asia/Kolkata')` to your timezone
3. Examples: 
   - `'America/New_York'` for EST
   - `'Europe/London'` for GMT
   - `'Asia/Dubai'` for GST

### **No Orders Found**
If there are no orders for tomorrow, the email won't be sent. This is intentional to avoid unnecessary emails.

### **PDF Generation Failed**
Check that reportlab is installed:
```bash
pip install reportlab==4.0.7
```

## Benefits for Manager

1. **Early Preparation**: Know what needs to be prepared the night before
2. **Stock Planning**: See all required items and quantities
3. **Payment Tracking**: Monitor due payments for next day deliveries
4. **Daily Planning**: Better organize the team and resources
5. **Email Archive**: Keep records of daily sales reports

## Dependencies

Required packages (all in `requirements.txt`):
- `APScheduler==3.10.4` - Task scheduling
- `pytz` - Timezone support (installed with APScheduler)
- `reportlab==4.0.7` - PDF generation
- `python-dotenv==1.0.0` - Environment configuration

## Security Notes

1. **Email Credentials**: Never commit `.env` file to version control
2. **SMTP Password**: Use app-specific passwords when available
3. **Manager Email**: Keep updated to ensure reports reach the right person
4. **Test Endpoint**: Consider adding authentication in production

## Future Enhancements

Potential improvements:
- [ ] Multiple recipient support
- [ ] Weekly summary reports
- [ ] SMS notifications
- [ ] WhatsApp integration
- [ ] Custom report templates
- [ ] Analytics dashboard link in email
- [ ] Low stock alerts
- [ ] Revenue comparison with previous days

## Support

For issues or questions:
1. Check server logs in terminal
2. Use test endpoint to verify email configuration
3. Review `.env` file settings
4. Ensure all dependencies are installed

---

**Note**: The daily email feature runs automatically when the Flask server is running. Make sure the server stays online for scheduled emails to be sent.
