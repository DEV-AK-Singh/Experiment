// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const crawlForm = document.getElementById('crawlForm');
    const urlInput = document.getElementById('urlInput');
    const depthSelect = document.getElementById('depthSelect');
    const crawlBtn = document.getElementById('crawlBtn');
    const loadingSection = document.getElementById('loadingSection');
    const resultSection = document.getElementById('resultSection');
    const statusText = document.getElementById('statusText');
    const pagesCount = document.getElementById('pagesCount');

    crawlForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        const maxDepth = parseInt(depthSelect.value);
        
        if (!url) {
            alert('Please enter a website URL');
            return;
        }

        // Validate URL format
        try {
            new URL(url);
        } catch {
            alert('Please enter a valid URL (include http:// or https://)');
            return;
        }

        await startCrawling(url, maxDepth);
    });

    async function startCrawling(url, maxDepth) {
        // Show loading state
        crawlBtn.disabled = true;
        crawlBtn.textContent = 'Crawling...';
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');

        statusText.textContent = 'Starting crawl...';
        pagesCount.textContent = '0';

        try {
            const response = await fetch('/deep-crawl', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    max_depth: maxDepth
                })
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data.report, data.domain);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            // Reset UI
            crawlBtn.disabled = false;
            crawlBtn.textContent = 'Start Deep Crawl';
            loadingSection.classList.add('hidden');
        }
    }

    function displayResults(report, domain) {
        const summary = report.crawl_summary;
        const pages = report.detailed_pages;

        let html = `
            <div class="summary-card">
                <h2>📊 Crawl Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>${summary.total_pages_crawled}</h3>
                        <p>Pages Crawled</p>
                    </div>
                    <div class="stat-card">
                        <h3>${summary.total_links_found}</h3>
                        <p>Total Links</p>
                    </div>
                    <div class="stat-card">
                        <h3>${summary.total_images_found}</h3>
                        <p>Images Found</p>
                    </div>
                    <div class="stat-card">
                        <h3>${summary.total_tables_found}</h3>
                        <p>Tables Found</p>
                    </div>
                    <div class="stat-card">
                        <h3>${summary.total_words_extracted}</h3>
                        <p>Words Extracted</p>
                    </div>
                    <div class="stat-card">
                        <h3>${summary.crawl_duration_seconds}s</h3>
                        <p>Crawl Time</p>
                    </div>
                </div>
            </div>

            <h2>📄 Pages Crawled (${Object.keys(pages).length})</h2>
        `;

        Object.keys(pages).forEach(pageKey => {
            const page = pages[pageKey];
            html += createPageItem(page);
        });

        // Add download button
        html += `
            <div style="text-align: center; margin-top: 30px;">
                <button onclick="downloadReport('${domain}')" style="background: #27ae60; padding: 15px 30px; font-size: 16px;">
                    📥 Download Full Report (JSON)
                </button>
            </div>
        `;

        resultSection.innerHTML = html;
        resultSection.classList.remove('hidden');
    }

    function createPageItem(page) {
        return `
            <div class="page-item">
                <h3><a href="${page.url}" target="_blank">${page.title}</a></h3>
                <p><strong>URL:</strong> ${page.url}</p>
                <p><strong>Stats:</strong> ${page.links_found} links, ${page.images_found} images, 
                   ${page.tables_found} tables, ${page.text_content.total_word_count} words</p>
                
                <details>
                    <summary>View Detailed Analysis</summary>
                    <div style="margin-top: 15px;">
                        <h4>Content Preview:</h4>
                        <textarea style="width: 100%; height: 120px; font-size: 12px; padding: 10px;" readonly>
${page.text_content.paragraphs.slice(0, 3).join('\n\n')}
                        </textarea>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                            <div>
                                <h5>Links (${page.links.length})</h5>
                                <ul style="font-size: 12px; max-height: 200px; overflow-y: auto;">
                                    ${page.links.slice(0, 5).map(link => 
                                        `<li>${link.text || 'No text'} → ${link.url}</li>`
                                    ).join('')}
                                </ul>
                                ${page.links.length > 5 ? `<p>... and ${page.links.length - 5} more links</p>` : ''}
                            </div>
                            <div>
                                <h5>Images (${page.images.length})</h5>
                                <ul style="font-size: 12px; max-height: 200px; overflow-y: auto;">
                                    ${page.images.slice(0, 3).map(img => 
                                        `<li>${img.alt || 'No alt'} → ${img.src}</li>`
                                    ).join('')}
                                </ul>
                                ${page.images.length > 3 ? `<p>... and ${page.images.length - 3} more images</p>` : ''}
                            </div>
                        </div>
                    </div>
                </details>
            </div>
        `;
    }

    function showError(message) {
        resultSection.innerHTML = `
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; text-align: center;">
                <h3>❌ Error</h3>
                <p>${message}</p>
            </div>
        `;
        resultSection.classList.remove('hidden');
    }

    // Make download function global
    window.downloadReport = async function(domain) {
        try {
            const response = await fetch('/download-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    domain: domain,
                    report: window.currentReport // You might want to store the report globally
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `crawl_report_${domain}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                alert('Download failed');
            }
        } catch (error) {
            alert('Download error: ' + error.message);
        }
    };
});