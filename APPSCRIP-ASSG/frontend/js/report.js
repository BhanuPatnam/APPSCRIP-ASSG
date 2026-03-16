document.addEventListener('DOMContentLoaded', () => {
    const reportData = JSON.parse(sessionStorage.getItem('current_report'));

    if (!reportData) {
        window.location.href = 'dashboard.html';
        return;
    }

    document.getElementById('report-sector').textContent = reportData.sector;
    document.getElementById('report-timestamp').innerHTML = `<i class="far fa-calendar-alt"></i> Generated: ${new Date(reportData.timestamp).toLocaleString()}`;
    document.getElementById('report-sources').innerHTML = `<i class="fas fa-database"></i> Sources: ${reportData.source_count}`;
    
    const reportBody = document.getElementById('report-body');
    reportBody.innerHTML = marked.parse(reportData.report_markdown);

    const wordCount = reportData.report_markdown.split(/\s+/).length;
    document.getElementById('report-words').innerHTML = `<i class="fas fa-file-alt"></i> Words: ${wordCount}`;

    generateTOC(reportBody);

    document.getElementById('download-pdf').addEventListener('click', () => window.print());
    document.getElementById('analyze-another').addEventListener('click', () => window.location.href = 'dashboard.html');
    document.getElementById('download-md').addEventListener('click', () => downloadAsMarkdown(reportData));
});

function generateTOC(contentElement) {
    const tocContainer = document.getElementById('toc');
    const headings = contentElement.querySelectorAll('h2, h3');
    const tocList = document.createElement('ul');

    headings.forEach(heading => {
        const id = heading.textContent.trim().toLowerCase().replace(/\s+/g, '-');
        heading.id = id;

        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${id}`;
        link.textContent = heading.textContent;
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });

    tocContainer.appendChild(tocList);
}

function downloadAsMarkdown(reportData) {
    const blob = new Blob([reportData.report_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportData.sector}_report.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
