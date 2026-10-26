async function runAudit() {
    const urlInput = document.getElementById('urlInput').value;
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results');
    const violationsList = document.getElementById('violationsList');
    const summary = document.getElementById('summary');
    const scoreBox = document.getElementById('scoreBox');

    if (!urlInput) {
        alert("Please enter a valid URL.");
        return;
    }

    loader.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    violationsList.innerHTML = '';
    scoreBox.innerHTML = '';

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
            summary.innerHTML = `<p><strong>Target:</strong> ${data.target_url} | <strong>Model Used:</strong> ${data.model_used}</p>`;
            
            // Score display logic with dynamic color coding
            const score = data.compliance_score;
            let scoreColor = '#34D399'; // Green
            if (score < 50) scoreColor = '#EF4444'; // Red
            else if (score < 80) scoreColor = '#F59E0B'; // Orange

            scoreBox.innerHTML = `
                <div style="background-color: #0F172A; border: 2px solid ${scoreColor}; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: ${scoreColor}; font-size: 1.5rem;">Accessibility Score: ${score}/100</h3>
                    <p style="margin: 5px 0 0 0; color: #94A3B8;">Detected ${data.violations_found} WCAG/RGAA compliance violations.</p>
                </div>
            `;

            data.violations.forEach(v => {
                const card = document.createElement('div');
                card.className = 'violation-card';
                card.innerHTML = `
                    <h3>${v.criterion}</h3>
                    <p><strong>Faulty Element:</strong> <code>${escapeHtml(v.element)}</code></p>
                    <p>${v.description}</p>
                    <p><strong>Recommended Code Fix:</strong></p>
                    <pre><code>${escapeHtml(v.fix_code)}</code></pre>
                `;
                violationsList.appendChild(card);
            });
        } else {
            summary.innerHTML = `<p style="color: red;">Error: ${data.message}</p>`;
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