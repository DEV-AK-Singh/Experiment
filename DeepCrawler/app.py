# app.py
from flask import Flask, request, jsonify, render_template, send_file
import os
import logging
from urllib.parse import urlparse

from src.crawler.deep_crawler import DeepWebCrawler
from src.utils.report_generator import ReportGenerator
from src.utils.file_utils import FileUtils
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOGS_DIR, 'crawler.log')),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route('/')
def home():
    """Main page"""
    return render_template('index.html')

@app.route('/deep-crawl', methods=['POST'])
def deep_crawl():
    """API endpoint for deep crawling"""
    data = request.get_json()
    url = data.get('url', '').strip()
    max_depth = data.get('max_depth', Config.MAX_DEPTH)
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'success': False, 'error': 'Invalid URL format'})
    except:
        return jsonify({'success': False, 'error': 'Invalid URL'})
    
    logging.info(f"🚀 Starting deep crawl: {url} (max depth: {max_depth})")
    
    try:
        # Perform crawling
        crawler = DeepWebCrawler(max_depth=max_depth)
        crawl_results = crawler.deep_crawl(url)
        
        if 'error' in crawl_results:
            logging.error(f"Crawling failed: {crawl_results['error']}")
            return jsonify({'success': False, 'error': crawl_results['error']})
        
        # Generate report
        report = ReportGenerator.generate_report(crawl_results)
        report_dict = report.to_dict()
        
        # Save report
        domain = crawl_results['base_domain']
        saved_path = FileUtils.save_report(report_dict, domain)
        
        logging.info(f"✅ Crawling completed: {crawl_results['total_pages_crawled']} pages crawled")
        
        return jsonify({
            'success': True,
            'report': report_dict,
            'saved_path': saved_path,
            'domain': domain
        })
        
    except Exception as e:
        logging.error(f"Unexpected error during crawling: {str(e)}")
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'})

@app.route('/download-report', methods=['POST'])
def download_report():
    """Download report as JSON file"""
    data = request.get_json()
    report_data = data.get('report')
    domain = data.get('domain', 'unknown')
    
    if not report_data:
        return jsonify({'success': False, 'error': 'No report data provided'})
    
    try:
        # Save export file
        filepath = FileUtils.save_export(report_data, domain)
        return send_file(filepath, as_attachment=True, download_name=f"crawl_report_{domain}.json")
    except Exception as e:
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'})

@app.route('/reports')
def list_reports():
    """List available reports"""
    reports = FileUtils.get_available_reports()
    return jsonify({'success': True, 'reports': reports})

if __name__ == '__main__':
    logging.info("🚀 Starting Deep Web Crawler Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)