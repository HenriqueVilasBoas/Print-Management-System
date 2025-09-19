#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Print Management System
Tests all backend endpoints with real data and error conditions
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any

class PrintManagementAPITester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.base_url = "http://localhost:8001"  # Default fallback
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=', 1)[1].strip()
                        break
        
        self.api_url = f"{self.base_url}/api"
        self.test_results = []
        self.uploaded_files = []
        self.created_jobs = []
        
        print(f"Testing backend at: {self.api_url}")
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "status": status
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "status" in data:
                    self.log_test("Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", False, "Invalid response format")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test file upload functionality"""
        try:
            # Test PDF upload
            pdf_path = "/app/test_sample.pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    files = {'files': ('test_document.pdf', f, 'application/pdf')}
                    response = requests.post(f"{self.api_url}/files/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if "files" in data and len(data["files"]) > 0:
                        uploaded_file = data["files"][0]
                        self.uploaded_files.append(uploaded_file["id"])
                        self.log_test("File Upload (PDF)", True, 
                                    f"Uploaded {uploaded_file['name']}, {uploaded_file['pages']} pages, {uploaded_file['size']}")
                        return True
                    else:
                        self.log_test("File Upload (PDF)", False, "No files in response")
                        return False
                else:
                    self.log_test("File Upload (PDF)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
            else:
                self.log_test("File Upload (PDF)", False, "Test PDF file not found")
                return False
                
        except Exception as e:
            self.log_test("File Upload (PDF)", False, f"Error: {str(e)}")
            return False
    
    def test_file_upload_excel(self):
        """Test Excel file upload"""
        try:
            # Test CSV upload (simulating Excel)
            csv_path = "/app/test_sample.csv"
            if os.path.exists(csv_path):
                with open(csv_path, 'rb') as f:
                    files = {'files': ('test_data.csv', f, 'text/csv')}
                    response = requests.post(f"{self.api_url}/files/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if "files" in data and len(data["files"]) > 0:
                        uploaded_file = data["files"][0]
                        self.uploaded_files.append(uploaded_file["id"])
                        self.log_test("File Upload (CSV)", True, 
                                    f"Uploaded {uploaded_file['name']}, {uploaded_file['size']}")
                        return True
                    else:
                        self.log_test("File Upload (CSV)", False, "No files in response")
                        return False
                else:
                    self.log_test("File Upload (CSV)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
            else:
                self.log_test("File Upload (CSV)", False, "Test CSV file not found")
                return False
                
        except Exception as e:
            self.log_test("File Upload (CSV)", False, f"Error: {str(e)}")
            return False
    
    def test_get_files(self):
        """Test retrieving file list"""
        try:
            response = requests.get(f"{self.api_url}/files", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "files" in data:
                    files_count = len(data["files"])
                    self.log_test("Get Files", True, f"Retrieved {files_count} files")
                    return True
                else:
                    self.log_test("Get Files", False, "No 'files' key in response")
                    return False
            else:
                self.log_test("Get Files", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Files", False, f"Error: {str(e)}")
            return False
    
    def test_update_file_copies(self):
        """Test updating file copies"""
        if not self.uploaded_files:
            self.log_test("Update File Copies", False, "No uploaded files to test with")
            return False
        
        try:
            file_id = self.uploaded_files[0]
            update_data = {"copies": 3}
            response = requests.put(f"{self.api_url}/files/{file_id}/copies", 
                                  json=update_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Update File Copies", True, f"Updated copies to 3 for file {file_id}")
                    return True
                else:
                    self.log_test("Update File Copies", False, "Invalid response format")
                    return False
            else:
                self.log_test("Update File Copies", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update File Copies", False, f"Error: {str(e)}")
            return False
    
    def test_reorder_files(self):
        """Test file reordering"""
        if len(self.uploaded_files) < 2:
            self.log_test("Reorder Files", False, "Need at least 2 files to test reordering")
            return False
        
        try:
            # Reverse the order of uploaded files
            reorder_data = {"file_ids": list(reversed(self.uploaded_files))}
            response = requests.put(f"{self.api_url}/files/reorder", 
                                  json=reorder_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and data.get("success"):
                    self.log_test("Reorder Files", True, "Files reordered successfully")
                    return True
                else:
                    self.log_test("Reorder Files", False, "Reorder operation failed")
                    return False
            else:
                self.log_test("Reorder Files", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Reorder Files", False, f"Error: {str(e)}")
            return False
    
    def test_get_printers(self):
        """Test getting available printers"""
        try:
            response = requests.get(f"{self.api_url}/printers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "printers" in data:
                    printers_count = len(data["printers"])
                    if printers_count > 0:
                        printer_names = [p["name"] for p in data["printers"]]
                        self.log_test("Get Printers", True, 
                                    f"Found {printers_count} printers: {', '.join(printer_names)}")
                        return data["printers"]
                    else:
                        self.log_test("Get Printers", False, "No printers found")
                        return []
                else:
                    self.log_test("Get Printers", False, "No 'printers' key in response")
                    return []
            else:
                self.log_test("Get Printers", False, f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("Get Printers", False, f"Error: {str(e)}")
            return []
    
    def test_printer_status(self, printer_id: str):
        """Test getting printer status"""
        try:
            response = requests.get(f"{self.api_url}/printers/status/{printer_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "printer_id" in data:
                    self.log_test("Get Printer Status", True, 
                                f"Printer {printer_id} status: {data['status']}")
                    return True
                else:
                    self.log_test("Get Printer Status", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Printer Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Printer Status", False, f"Error: {str(e)}")
            return False
    
    def test_create_print_job(self, printer_id: str):
        """Test creating print job"""
        if not self.uploaded_files:
            self.log_test("Create Print Job", False, "No uploaded files to create job with")
            return None
        
        try:
            job_data = {
                "files": self.uploaded_files[:1],  # Use first uploaded file
                "printer_id": printer_id,
                "settings": {
                    "color_mode": "color",
                    "paper_size": "A4",
                    "orientation": "portrait",
                    "quality": "standard",
                    "duplex": "none"
                }
            }
            
            response = requests.post(f"{self.api_url}/print-jobs", 
                                   json=job_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "job" in data:
                    job = data["job"]
                    job_id = job["id"]
                    self.created_jobs.append(job_id)
                    self.log_test("Create Print Job", True, 
                                f"Created job {job_id} with {job['total_pages']} pages")
                    return job_id
                else:
                    self.log_test("Create Print Job", False, "No 'job' key in response")
                    return None
            else:
                self.log_test("Create Print Job", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Print Job", False, f"Error: {str(e)}")
            return None
    
    def test_start_print_job(self, job_id: str):
        """Test starting print job"""
        try:
            response = requests.post(f"{self.api_url}/print-jobs/{job_id}/start", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Start Print Job", True, f"Started job {job_id}")
                    return True
                else:
                    self.log_test("Start Print Job", False, "Invalid response format")
                    return False
            else:
                self.log_test("Start Print Job", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Start Print Job", False, f"Error: {str(e)}")
            return False
    
    def test_get_job_status(self, job_id: str):
        """Test getting job status"""
        try:
            response = requests.get(f"{self.api_url}/print-jobs/{job_id}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "job_id" in data:
                    self.log_test("Get Job Status", True, 
                                f"Job {job_id} status: {data['status']}")
                    return True
                else:
                    self.log_test("Get Job Status", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Job Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Job Status", False, f"Error: {str(e)}")
            return False
    
    def test_combined_print_start(self, printer_id: str):
        """Test combined create and start print job"""
        if not self.uploaded_files:
            self.log_test("Combined Print Start", False, "No uploaded files to test with")
            return False
        
        try:
            job_data = {
                "files": self.uploaded_files[:1],  # Use first uploaded file
                "printer_id": printer_id,
                "settings": {
                    "color_mode": "bw",
                    "paper_size": "A4",
                    "orientation": "portrait",
                    "quality": "high",
                    "duplex": "none"
                }
            }
            
            response = requests.post(f"{self.api_url}/print/start", 
                                   json=job_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data and "total_pages" in data:
                    self.log_test("Combined Print Start", True, 
                                f"Created and started job {data['job_id']} with {data['total_pages']} pages")
                    return True
                else:
                    self.log_test("Combined Print Start", False, "Invalid response format")
                    return False
            else:
                self.log_test("Combined Print Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Combined Print Start", False, f"Error: {str(e)}")
            return False
    
    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats/dashboard", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_files", "total_pages", "total_print_jobs", "success_rate"]
                if all(field in data for field in required_fields):
                    self.log_test("Dashboard Stats", True, 
                                f"Stats: {data['total_files']} files, {data['total_pages']} pages, "
                                f"{data['total_print_jobs']} jobs, {data['success_rate']}% success")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Dashboard Stats", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Error: {str(e)}")
            return False
    
    def test_print_history(self):
        """Test print history retrieval"""
        try:
            response = requests.get(f"{self.api_url}/print-history?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "history" in data:
                    history_count = len(data["history"])
                    self.log_test("Print History", True, f"Retrieved {history_count} history items")
                    return True
                else:
                    self.log_test("Print History", False, "No 'history' key in response")
                    return False
            else:
                self.log_test("Print History", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Print History", False, f"Error: {str(e)}")
            return False
    
    def test_get_settings(self):
        """Test getting system settings"""
        try:
            response = requests.get(f"{self.api_url}/settings", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["default_settings", "file_retention_days", "max_file_size_mb", "supported_file_types"]
                if all(field in data for field in required_fields):
                    self.log_test("Get Settings", True, 
                                f"Max file size: {data['max_file_size_mb']}MB, "
                                f"Retention: {data['file_retention_days']} days")
                    return data
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Get Settings", False, f"Missing fields: {missing}")
                    return None
            else:
                self.log_test("Get Settings", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Get Settings", False, f"Error: {str(e)}")
            return None
    
    def test_update_settings(self):
        """Test updating system settings"""
        try:
            # First get current settings
            current_settings = self.test_get_settings()
            if not current_settings:
                self.log_test("Update Settings", False, "Could not get current settings")
                return False
            
            # Update some settings
            updated_settings = current_settings.copy()
            updated_settings["max_file_size_mb"] = 150
            updated_settings["file_retention_days"] = 45
            
            response = requests.put(f"{self.api_url}/settings", 
                                  json=updated_settings, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("max_file_size_mb") == 150 and data.get("file_retention_days") == 45:
                    self.log_test("Update Settings", True, 
                                "Updated max file size to 150MB and retention to 45 days")
                    return True
                else:
                    self.log_test("Update Settings", False, "Settings not updated correctly")
                    return False
            else:
                self.log_test("Update Settings", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update Settings", False, f"Error: {str(e)}")
            return False
    
    def test_file_size_validation(self):
        """Test file size validation"""
        try:
            # Create a large dummy file content (simulate oversized file)
            large_content = b"x" * (200 * 1024 * 1024)  # 200MB content
            
            files = {'files': ('large_file.pdf', large_content, 'application/pdf')}
            response = requests.post(f"{self.api_url}/files/upload", files=files, timeout=60)
            
            if response.status_code == 400:
                error_data = response.json()
                if "exceeds maximum size" in error_data.get("detail", ""):
                    self.log_test("File Size Validation", True, "Large file correctly rejected")
                    return True
                else:
                    self.log_test("File Size Validation", False, f"Unexpected error: {error_data}")
                    return False
            else:
                self.log_test("File Size Validation", False, 
                            f"Large file should be rejected but got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("File Size Validation", False, f"Error: {str(e)}")
            return False
    
    def test_delete_file(self):
        """Test file deletion"""
        if not self.uploaded_files:
            self.log_test("Delete File", False, "No uploaded files to delete")
            return False
        
        try:
            file_id = self.uploaded_files[-1]  # Delete last uploaded file
            response = requests.delete(f"{self.api_url}/files/{file_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.uploaded_files.remove(file_id)
                    self.log_test("Delete File", True, f"Deleted file {file_id}")
                    return True
                else:
                    self.log_test("Delete File", False, "Invalid response format")
                    return False
            else:
                self.log_test("Delete File", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Delete File", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid file ID
            response = requests.get(f"{self.api_url}/files/invalid-id/copies", timeout=10)
            if response.status_code == 404:
                self.log_test("Error Handling (Invalid File ID)", True, "404 returned for invalid file ID")
            else:
                self.log_test("Error Handling (Invalid File ID)", False, 
                            f"Expected 404 but got {response.status_code}")
            
            # Test invalid printer ID
            response = requests.get(f"{self.api_url}/printers/status/invalid-printer", timeout=10)
            if response.status_code in [200, 404]:  # Either is acceptable
                self.log_test("Error Handling (Invalid Printer ID)", True, 
                            f"Handled invalid printer ID with {response.status_code}")
            else:
                self.log_test("Error Handling (Invalid Printer ID)", False, 
                            f"Unexpected status {response.status_code}")
            
            # Test invalid job ID
            response = requests.get(f"{self.api_url}/print-jobs/invalid-job/status", timeout=10)
            if response.status_code == 404:
                self.log_test("Error Handling (Invalid Job ID)", True, "404 returned for invalid job ID")
            else:
                self.log_test("Error Handling (Invalid Job ID)", False, 
                            f"Expected 404 but got {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("PRINT MANAGEMENT SYSTEM - BACKEND API TESTS")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("\n❌ CRITICAL: Backend is not accessible. Stopping tests.")
            return self.generate_report()
        
        # File management tests
        print("\n📁 FILE MANAGEMENT TESTS")
        print("-" * 30)
        self.test_file_upload()
        self.test_file_upload_excel()
        self.test_get_files()
        self.test_update_file_copies()
        self.test_reorder_files()
        self.test_file_size_validation()
        self.test_delete_file()
        
        # Printer management tests
        print("\n🖨️  PRINTER MANAGEMENT TESTS")
        print("-" * 30)
        printers = self.test_get_printers()
        if printers:
            self.test_printer_status(printers[0]["id"])
        
        # Print job tests
        print("\n📋 PRINT JOB TESTS")
        print("-" * 30)
        if printers and self.uploaded_files:
            job_id = self.test_create_print_job(printers[0]["id"])
            if job_id:
                time.sleep(1)  # Brief pause
                self.test_start_print_job(job_id)
                time.sleep(2)  # Wait for job processing
                self.test_get_job_status(job_id)
            
            self.test_combined_print_start(printers[0]["id"])
        
        # Dashboard and stats tests
        print("\n📊 DASHBOARD & STATISTICS TESTS")
        print("-" * 30)
        self.test_dashboard_stats()
        self.test_print_history()
        
        # Settings tests
        print("\n⚙️  SETTINGS TESTS")
        print("-" * 30)
        self.test_get_settings()
        self.test_update_settings()
        
        # Error handling tests
        print("\n🚨 ERROR HANDLING TESTS")
        print("-" * 30)
        self.test_error_handling()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        success_rate = (passed / len(self.test_results) * 100) if self.test_results else 0
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS ({failed}):")
            print("-" * 30)
            for result in self.test_results:
                if not result["success"]:
                    print(f"• {result['test']}: {result['details']}")
        
        if passed > 0:
            print(f"\n✅ PASSED TESTS ({passed}):")
            print("-" * 30)
            for result in self.test_results:
                if result["success"]:
                    print(f"• {result['test']}")
        
        return {
            "total": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = PrintManagementAPITester()
    report = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if report["failed"] > 0:
        exit(1)
    else:
        print("\n🎉 All tests passed!")
        exit(0)