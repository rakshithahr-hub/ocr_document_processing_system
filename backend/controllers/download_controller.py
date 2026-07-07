# controllers/download_controller.py - Add detailed logging

import os
import json
import logging
from flask import send_file, jsonify, request, current_app
from config import Config
import mimetypes
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DownloadController:
    
    @staticmethod
    def list_output_files():
        """List all output files (txt, pdf, json)"""
        try:
            output_folder = Config.OUTPUT_FOLDER
            logger.info(f"📁 Listing files in: {output_folder}")
            
            if not os.path.exists(output_folder):
                logger.warning(f"⚠️ Output folder does not exist: {output_folder}")
                return jsonify({'files': [], 'total': 0})
            
            files = []
            file_dict = {}
            
            for filename in os.listdir(output_folder):
                file_path = os.path.join(output_folder, filename)
                if os.path.isfile(file_path):
                    name, ext = os.path.splitext(filename)
                    if name not in file_dict:
                        file_dict[name] = {}
                    file_dict[name][ext[1:]] = {
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    }
            
            for name, extensions in file_dict.items():
                files.append({
                    'name': name,
                    'extensions': extensions
                })
            
            logger.info(f"✅ Found {len(files)} file groups")
            return jsonify({
                'files': files,
                'total': len(files)
            })
            
        except Exception as e:
            logger.error(f"❌ Error listing files: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_file(filename):
        """Download a specific file with format parameter"""
        try:
            format_type = request.args.get('format', 'txt').lower()
            logger.info(f"📥 Downloading {filename}.{format_type}")
            
            supported_formats = ['txt', 'pdf', 'json']
            if format_type not in supported_formats:
                return jsonify({'error': f'Unsupported format. Supported: {supported_formats}'}), 400
            
            # Clean filename - remove any path separators
            clean_filename = os.path.basename(filename)
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.{format_type}")
            
            logger.info(f"📂 Looking for: {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ File not found: {file_path}")
                # List available files for debugging
                if os.path.exists(Config.OUTPUT_FOLDER):
                    available = os.listdir(Config.OUTPUT_FOLDER)
                    logger.info(f"📁 Available files: {available}")
                return jsonify({
                    'error': f'File not found: {clean_filename}.{format_type}',
                    'available_files': os.listdir(Config.OUTPUT_FOLDER) if os.path.exists(Config.OUTPUT_FOLDER) else []
                }), 404
            
            mime_types = {
                'txt': 'text/plain',
                'pdf': 'application/pdf',
                'json': 'application/json'
            }
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{clean_filename}.{format_type}",
                mimetype=mime_types.get(format_type, 'application/octet-stream')
            )
            
        except Exception as e:
            logger.error(f"❌ Download error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def delete_file(filename):
        """Delete a specific file"""
        try:
            format_type = request.args.get('format', 'txt').lower()
            clean_filename = os.path.basename(filename)
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.{format_type}")
            
            if not os.path.exists(file_path):
                return jsonify({'error': f'File not found: {clean_filename}.{format_type}'}), 404
            
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'message': f'File deleted: {clean_filename}.{format_type}'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_txt(filename):
        """Download TXT file"""
        try:
            clean_filename = os.path.basename(filename)
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.txt")
            logger.info(f"📥 Downloading TXT: {file_path}")
            
            if not os.path.exists(file_path):
                logger.error(f"❌ TXT file not found: {file_path}")
                return jsonify({'error': f'File not found: {clean_filename}.txt'}), 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{clean_filename}.txt",
                mimetype='text/plain'
            )
        except Exception as e:
            logger.error(f"❌ TXT download error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_pdf(filename):
        """Download PDF file"""
        try:
            clean_filename = os.path.basename(filename)
            logger.info(f"📥 Downloading PDF: {clean_filename}")
            
            # Check if filename has extension and remove it
            if '.' in clean_filename:
                clean_filename = clean_filename.rsplit('.', 1)[0]
                logger.info(f"📝 Stripped extension: {clean_filename}")
            
            # Look for PDF file
            pdf_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.pdf")
            logger.info(f"📂 Looking for PDF at: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                logger.warning(f"⚠️ PDF not found: {pdf_path}")
                
                # Try to find the PDF with different naming patterns
                possible_names = [
                    f"{clean_filename}.pdf",
                    f"{clean_filename}_ocr.pdf",
                    f"{clean_filename}_output.pdf",
                    f"{clean_filename}_result.pdf"
                ]
                
                found = False
                for name in possible_names:
                    test_path = os.path.join(Config.OUTPUT_FOLDER, name)
                    if os.path.exists(test_path):
                        pdf_path = test_path
                        found = True
                        logger.info(f"✅ Found PDF at: {pdf_path}")
                        break
                
                if not found:
                    # Check if TXT exists and generate PDF from it
                    txt_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.txt")
                    logger.info(f"📂 Checking for TXT at: {txt_path}")
                    
                    if os.path.exists(txt_path):
                        logger.info("✅ TXT found, generating PDF...")
                        try:
                            from reportlab.lib.pagesizes import letter
                            from reportlab.pdfgen import canvas
                            from reportlab.lib.units import inch
                            import textwrap
                            
                            with open(txt_path, 'r', encoding='utf-8') as f:
                                text = f.read()
                            
                            c = canvas.Canvas(pdf_path, pagesize=letter)
                            width, height = letter
                            c.setFont('Helvetica', 10)
                            
                            y = height - 1 * inch
                            margin = 1 * inch
                            line_height = 14
                            
                            lines = text.split('\n')
                            for line in lines:
                                wrapped_lines = textwrap.wrap(line, width=90)
                                if not wrapped_lines:
                                    wrapped_lines = ['']
                                
                                for wrapped_line in wrapped_lines:
                                    if y < 0.5 * inch:
                                        c.showPage()
                                        y = height - 1 * inch
                                        c.setFont('Helvetica', 10)
                                    
                                    c.drawString(margin, y, wrapped_line)
                                    y -= line_height
                            
                            c.save()
                            logger.info(f"✅ PDF generated: {pdf_path}")
                        except ImportError:
                            logger.error("❌ reportlab not installed")
                            return jsonify({
                                'error': 'PDF generation requires reportlab. Install with: pip install reportlab'
                            }), 500
                        except Exception as e:
                            logger.error(f"❌ PDF generation failed: {e}")
                            return jsonify({
                                'error': f'PDF generation failed: {str(e)}'
                            }), 500
                    else:
                        # List all files in output folder for debugging
                        if os.path.exists(Config.OUTPUT_FOLDER):
                            available_files = os.listdir(Config.OUTPUT_FOLDER)
                            logger.info(f"📁 Available files in {Config.OUTPUT_FOLDER}: {available_files}")
                            return jsonify({
                                'error': f'PDF file not found: {clean_filename}.pdf',
                                'available_files': available_files,
                                'suggested_filenames': [f for f in available_files if clean_filename in f]
                            }), 404
                        else:
                            return jsonify({'error': f'Output folder not found: {Config.OUTPUT_FOLDER}'}), 404
            
            logger.info(f"✅ Sending PDF: {pdf_path}")
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"{clean_filename}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            logger.error(f"❌ PDF download error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_json(filename):
        """Download JSON file"""
        try:
            clean_filename = os.path.basename(filename)
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{clean_filename}.json")
            logger.info(f"📥 Downloading JSON: {file_path}")
            
            if not os.path.exists(file_path):
                logger.error(f"❌ JSON file not found: {file_path}")
                return jsonify({'error': f'File not found: {clean_filename}.json'}), 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{clean_filename}.json",
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"❌ JSON download error: {str(e)}")
            return jsonify({'error': str(e)}), 500