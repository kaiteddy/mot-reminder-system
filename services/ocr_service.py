"""
OCR Module for MOT Reminder System

This module provides OCR (Optical Character Recognition) functionality
to extract vehicle registration numbers from images or scanned documents.
It includes validation, correction, and DVLA verification capabilities.
"""

import cv2
import numpy as np
import pytesseract
import re
import os
from PIL import Image
from services.dvla_api_service import DVLAApiService

class OCRService:
    def __init__(self):
        """Initialize the OCR service with necessary configurations."""
        # Set pytesseract path if needed (uncomment and modify for Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.dvla_api = DVLAApiService()
        
        # UK registration plate patterns
        self.uk_plate_patterns = [
            r'^[A-Z]{2}[0-9]{2}\s*[A-Z]{3}$',  # Modern format: AB12 CDE
            r'^[A-Z][0-9]{1,3}\s*[A-Z]{3}$',    # Older format: A123 BCD
            r'^[A-Z]{3}\s*[0-9]{1,3}[A-Z]$',    # Reversed older format: ABC 123D
            r'^[A-Z]{1,2}[0-9]{1,4}$',          # Very old format: AB1234
            r'^[0-9]{1,4}[A-Z]{1,2}$'           # Very old reversed format: 1234AB
        ]
        
        # Common OCR errors in registration plates
        self.common_errors = {
            '0': 'O',
            'O': '0',
            '1': 'I',
            'I': '1',
            '5': 'S',
            'S': '5',
            '8': 'B',
            'B': '8',
            'Z': '2',
            '2': 'Z',
            'G': '6',
            '6': 'G',
            'D': '0',
            'Q': '0'
        }
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised
    
    def extract_text_from_image(self, image_path):
        """
        Extract all text from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        try:
            # Preprocess image
            preprocessed = self.preprocess_image(image_path)
            
            # Apply OCR
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(preprocessed, config=custom_config)
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def extract_registration_from_text(self, text):
        """
        Extract vehicle registration numbers from text.
        
        Args:
            text: Text containing potential registration numbers
            
        Returns:
            List of potential registration numbers
        """
        # Remove spaces and convert to uppercase
        text = text.upper()
        
        # Split text into lines and words
        lines = text.split('\n')
        words = []
        for line in lines:
            words.extend(line.split())
        
        # Remove spaces within words (e.g., "AB 12CDE" -> "AB12CDE")
        words = [re.sub(r'\s+', '', word) for word in words]
        
        # Filter words that match UK registration plate patterns
        potential_registrations = []
        for word in words:
            # Skip very short or very long strings
            if len(word) < 3 or len(word) > 8:
                continue
                
            # Check against patterns
            for pattern in self.uk_plate_patterns:
                if re.match(pattern, word):
                    potential_registrations.append(word)
                    break
            
            # Try common error corrections if no match
            if word not in potential_registrations:
                corrected = self.try_error_corrections(word)
                for correction in corrected:
                    for pattern in self.uk_plate_patterns:
                        if re.match(pattern, correction) and correction not in potential_registrations:
                            potential_registrations.append(correction)
                            break
        
        return potential_registrations
    
    def try_error_corrections(self, text):
        """
        Try common OCR error corrections for registration plates.
        
        Args:
            text: Text to correct
            
        Returns:
            List of possible corrections
        """
        corrections = [text]
        
        # Try replacing each character with its common error alternative
        for i, char in enumerate(text):
            if char in self.common_errors:
                corrected = text[:i] + self.common_errors[char] + text[i+1:]
                corrections.append(corrected)
        
        # Try more complex corrections for specific cases
        # Remove spaces
        corrections.append(text.replace(' ', ''))
        
        # Fix common pattern errors
        if len(text) >= 7:  # Modern format length
            # Try inserting space after first 4 characters
            corrections.append(text[:4] + ' ' + text[4:])
        
        return corrections
    
    def format_registration(self, registration):
        """
        Format registration to standard format.
        
        Args:
            registration: Registration number
            
        Returns:
            Formatted registration
        """
        # Remove all spaces
        reg = registration.replace(' ', '')
        
        # Format based on length
        if len(reg) == 7:  # Modern format
            return reg[:4] + ' ' + reg[4:]
        elif len(reg) == 6 and reg[0].isalpha() and reg[1].isdigit():  # Old format A123BCD
            return reg[:4] + ' ' + reg[4:]
        elif len(reg) == 6 and reg[0].isalpha() and reg[1].isalpha() and reg[2].isdigit():  # Old format AB12CDE
            return reg[:4] + ' ' + reg[4:]
        
        # Return as is if no formatting rule applies
        return reg
    
    def verify_with_dvla(self, registration):
        """
        Verify registration with DVLA API.
        
        Args:
            registration: Registration number to verify
            
        Returns:
            Tuple of (is_valid, vehicle_data)
        """
        try:
            # Remove spaces for API call
            reg = registration.replace(' ', '')
            
            # Call DVLA API
            vehicle_data = self.dvla_api.get_vehicle_details(reg)
            
            # Check if data was returned
            if vehicle_data and 'registrationNumber' in vehicle_data:
                return True, vehicle_data
            
            return False, None
        except Exception as e:
            print(f"Error verifying registration with DVLA: {e}")
            return False, None
    
    def process_image(self, image_path):
        """
        Process an image to extract and verify registration numbers.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extraction results
        """
        results = {
            'original_text': '',
            'potential_registrations': [],
            'verified_registrations': [],
            'best_match': None
        }
        
        # Extract text
        text = self.extract_text_from_image(image_path)
        results['original_text'] = text
        
        # Extract potential registrations
        potential_regs = self.extract_registration_from_text(text)
        
        # Format and verify each potential registration
        verified_regs = []
        for reg in potential_regs:
            formatted_reg = self.format_registration(reg)
            is_valid, vehicle_data = self.verify_with_dvla(formatted_reg)
            
            reg_info = {
                'registration': formatted_reg,
                'is_valid': is_valid,
                'vehicle_data': vehicle_data
            }
            
            results['potential_registrations'].append(formatted_reg)
            
            if is_valid:
                verified_regs.append(reg_info)
                results['verified_registrations'].append(formatted_reg)
        
        # Determine best match (first verified registration)
        if verified_regs:
            results['best_match'] = verified_regs[0]
        
        return results
