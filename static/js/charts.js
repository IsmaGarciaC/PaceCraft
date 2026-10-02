document.addEventListener("DOMContentLoaded", async function() {
    const canvas = document.getElementById('paceChart');
    if (!canvas) return; // Exit if not on the dashboard or if canvas doesn't exist

    try {
        // Fetch JSON data from our FastAPI backend
        const response = await fetch('/api/chart-data');
        if (!response.ok) throw new Error("Failed to fetch chart data");
        
        const data = await response.json();
        
        // Ensure there is data to display
        if (data.labels.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-muted text-center mt-5">Not enough data to display chart.</p>';
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Initialize Chart.js
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Average Pace (min/km)',
                    data: data.paces,
                    borderColor: 'rgba(37, 99, 235, 1)', // Bootstrap Primary blue
                    backgroundColor: 'rgba(37, 99, 235, 0.2)', // Light blue fill
                    borderWidth: 2,
                    tension: 0.3, // Makes the line smooth/curved
                    fill: true,
                    pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        // In running, a lower pace (e.g. 4:30) is faster/better than a higher pace (e.g. 6:00).
                        // So we reverse the Y axis so the line goes UP as you get FASTER.
                        reverse: true, 
                        title: {
                            display: true,
                            text: 'Pace (min/km)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            // Custom tooltip formatting to show "5:30 /km" instead of "5.5"
                            label: function(context) {
                                let pace = context.parsed.y;
                                let mins = Math.floor(pace);
                                let secs = Math.round((pace - mins) * 60);
                                if (secs === 60) { mins++; secs = 0; }
                                
                                // padStart ensures seconds are two digits (e.g., '05' instead of '5')
                                let formattedSecs = secs.toString().padStart(2, '0');
                                return ` Pace: ${mins}:${formattedSecs} /km`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error loading chart:", error);
    }
});
