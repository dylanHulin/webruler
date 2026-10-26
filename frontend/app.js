async function runAudit() {
    const urlInput = document.getElementById('urlInput').value;
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results');
    const violationsList = document.getElementById('violationsList');
    const summary = document.getElementById('summary');

    if (!urlInput) {
        alert("Please enter a valid URL.");
        return;
    }

    // UI Reset
    loader.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    violationsList.innerHTML = '';

    try {
        const response = await fetch('http://localhost:8000/api/audit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: urlInput })
        });

        const data = await response.json();
        loader.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        if (data.status === 'success') {
            summary.innerHTML = `<p><strong>Target:</strong> ${data.target_url} | <strong>Model:</strong> ${data.model_used} | <strong>Violations Found:</strong> ${data.violations_found}</p>`;
            
            data.violations.forEach(v => {
                const card = document.createElement('div');
                card.className = 'violation-card';
                card.innerHTML = `
                    <h3>${v.criterion}</h3>
                    <p><strong>Element:</strong> <code>${escapeHtml(v.element)}</code></p>
                    <p>${v.description}</p>
                    <p><strong>Recommended Code Fix:</strong></p>
                    <pre><code>${escapeHtml(v.fix_code)}</code></pre>
                `;
                violationsList.appendChild(card);
            });
        } else {
            summary.innerHTML = `<p style="color: red;">Error during audit execution.</p>`;
        }
    } catch (error) {
        loader.classList.add('hidden');
        alert("Failed to connect to backend server. Make sure FastAPI is running.");
        console.error(error);
    }
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}