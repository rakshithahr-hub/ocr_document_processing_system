from flask import send_file, jsonify, request
import os
import json
from config import Config
import mimetypes
from datetime import datetime

class DownloadController:
    
    @staticmethod
    def list_output_files():
        """List all output files (txt, pdf, json)"""
        try:
            output_folder = Config.OUTPUT_FOLDER
            if not os.path.exists(output_folder):
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
            
            return jsonify({
                'files': files,
                'total': len(files)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_file(filename):
        """Download a specific file with format parameter"""
        try:
            format_type = request.args.get('format', 'txt').lower()
            
            supported_formats = ['txt', 'pdf', 'json']
            if format_type not in supported_formats:
                return jsonify({'error': f'Unsupported format. Supported: {supported_formats}'}), 400
            
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.{format_type}")
            
            if not os.path.exists(file_path):
                return jsonify({'error': f'File not found: {filename}.{format_type}'}), 404
            
            mime_types = {
                'txt': 'text/plain',
                'pdf': 'application/pdf',
                'json': 'application/json'
            }
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{filename}.{format_type}",
                mimetype=mime_types.get(format_type, 'application/octet-stream')
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def delete_file(filename):
        """Delete a specific file"""
        try:
            format_type = request.args.get('format', 'txt').lower()
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.{format_type}")
            
            if not os.path.exists(file_path):
                return jsonify({'error': f'File not found: {filename}.{format_type}'}), 404
            
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'message': f'File deleted: {filename}.{format_type}'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_txt(filename):
        """Download TXT file"""
        try:
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.txt")
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{filename}.txt",
                mimetype='text/plain'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_pdf(filename):
        """Download PDF file"""
        try:
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.pdf")
            if not os.path.exists(file_path):
                # Try to generate PDF from TXT
                txt_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.txt")
                if os.path.exists(txt_path):
                    # Simple PDF generation using reportlab
                    try:
                        from reportlab.lib.pagesizes import letter
                        from reportlab.pdfgen import canvas
                        from reportlab.lib.units import inch
                        import textwrap
                        
                        pdf_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.pdf")
                        
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
                        
                        return send_file(
                            pdf_path,
                            as_attachment=True,
                            download_name=f"{filename}.pdf",
                            mimetype='application/pdf'
                        )
                    except ImportError:
                        return jsonify({
                            'error': 'PDF generation requires reportlab. Install with: pip install reportlab'
                        }), 500
                return jsonify({'error': 'File not found'}), 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{filename}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    def download_json(filename):
        """Download JSON file"""
        try:
            file_path = os.path.join(Config.OUTPUT_FOLDER, f"{filename}.json")
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{filename}.json",
                mimetype='application/json'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500