# Print Management System - Backend Integration Contracts

## API Endpoints Required

### 1. File Management Endpoints
- `POST /api/files/upload` - Upload multiple files
- `GET /api/files` - Get all files in print queue
- `DELETE /api/files/{file_id}` - Remove file from queue
- `PUT /api/files/{file_id}/copies` - Update file copies count
- `PUT /api/files/reorder` - Reorder files in queue

### 2. Printer Management Endpoints
- `GET /api/printers` - Get available printers
- `GET /api/printers/status` - Get printer status
- `POST /api/print/start` - Start print job

### 3. Dashboard/Statistics Endpoints
- `GET /api/stats/dashboard` - Get dashboard statistics
- `GET /api/print-history` - Get recent print history

### 4. Settings Endpoints
- `GET /api/settings` - Get system settings
- `PUT /api/settings` - Update system settings

### 5. Print Job Management
- `POST /api/print-jobs` - Create new print job
- `GET /api/print-jobs/{job_id}/status` - Get print job status

## Data Models

### File Model
```json
{
  "id": "string",
  "name": "string",
  "originalName": "string",
  "type": "string", // PDF, Excel, etc.
  "size": "string", // "2.4 MB"
  "sizeBytes": "number",
  "pages": "number",
  "copies": "number",
  "dateAdded": "string", // ISO date
  "path": "string", // file storage path
  "metadata": {
    "createdDate": "string",
    "modifiedDate": "string"
  }
}
```

### Printer Model
```json
{
  "id": "string",
  "name": "string",
  "status": "Ready|Offline|Busy|Error|Low Toner",
  "isDefault": "boolean",
  "capabilities": {
    "color": "boolean",
    "duplex": "boolean",
    "paperSizes": ["A4", "A3", "Letter"]
  }
}
```

### Print Job Model
```json
{
  "id": "string",
  "files": ["file_id1", "file_id2"],
  "printer": "printer_id",
  "settings": {
    "colorMode": "color|bw",
    "paperSize": "A4|A3",
    "orientation": "portrait|landscape",
    "quality": "draft|standard|high|best",
    "duplex": "none|long|short"
  },
  "status": "pending|printing|completed|failed",
  "createdAt": "string",
  "completedAt": "string",
  "totalPages": "number"
}
```

### Settings Model
```json
{
  "defaultPrinter": "string",
  "defaultSettings": {
    "colorMode": "color",
    "paperSize": "A4",
    "orientation": "portrait",
    "quality": "standard"
  },
  "fileRetentionDays": "number",
  "maxFileSize": "number", // in MB
  "supportedFileTypes": ["PDF", "XLSX", "XLS", "DOC", "DOCX"]
}
```

## Frontend Changes Required

### 1. Replace Mock Data
- Remove mockData.js usage in FileManager component
- Connect to real API endpoints for file operations
- Update Dashboard to fetch real statistics

### 2. File Upload Implementation
- Replace mock "Add Files" with real file input dialog
- Handle multiple file selection
- Show upload progress
- Extract and display real file metadata

### 3. Add Settings Component
- Create new Settings tab in navigation
- Allow configuration of default print settings
- File retention settings
- Supported file types management

### 4. Real Printer Integration
- Fetch actual available printers from system
- Show real printer status and capabilities
- Handle printer-specific settings

## Backend Implementation Strategy

### 1. File Storage
- Store uploaded files in `/app/backend/uploads/` directory
- Generate unique IDs for files to prevent conflicts
- Extract metadata using appropriate libraries (PyPDF2 for PDFs, openpyxl for Excel)

### 2. Printer Detection
- Use Python's `win32print` library (Windows) or `cups` (Linux/Mac)
- Fallback to mock printers in web environment
- Cache printer information to improve performance

### 3. Print Job Processing
- Queue print jobs in database
- Use system print commands or libraries to execute printing
- Track job status and update database

### 4. Database Schema
- Files table: store file metadata and queue information
- Print_jobs table: track print job history and status
- Settings table: store system configuration
- Print_history table: maintain printing statistics

## Error Handling

### File Upload Errors
- File too large
- Unsupported file type
- Disk space issues
- File corruption

### Printer Errors
- Printer offline
- No printers available
- Print job failed
- Insufficient permissions

### System Errors
- Database connection issues
- File system errors
- Network connectivity problems

## Security Considerations
- File type validation on upload
- File size limits
- Secure file storage with proper permissions
- Input sanitization for all API endpoints