import http.server
import socketserver
import psutil
import time
from prometheus_client import CollectorRegistry, Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST

PORT = 8000

start_time = time.time()
request_count = 0
last_request_time = None

# Prometheus metrics
registry = CollectorRegistry()
cpu_gauge = Gauge('python_app_cpu_percent', 'CPU usage percent', registry=registry)
mem_gauge = Gauge('python_app_memory_percent', 'Memory usage percent', registry=registry)
requests_counter = Counter('python_app_requests_total', 'Total HTTP requests', registry=registry)
uptime_gauge = Gauge('python_app_uptime_seconds', 'App uptime seconds', registry=registry)

STYLE = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        :root {
            --bg-color: #f0f4f8;
            --container-bg: #ffffff;
            --card-bg: #ffffff;
            --card-hover-bg: #f5f9ff;
            --text-color: #333333;
            --primary-accent: #007bff;
            --secondary-accent: #28a745;
            --highlight-color: #e8f3ff;
            --shadow-color: rgba(0, 0, 0, 0.1);
            --border-color: #e0e0e0;
        }

        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 40px;
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: background-color 0.3s;
        }
        .container {
            background: var(--container-bg);
            padding: 30px 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px var(--shadow-color);
            max-width: 1100px;
            margin: 20px auto;
            border: 1px solid var(--border-color);
            transition: box-shadow 0.3s;
        }
        h1, h2, h3 {
            color: var(--primary-accent);
            text-align: center;
            margin-bottom: 25px;
            font-weight: 500;
        }
        p {
            font-size: 1rem;
            line-height: 1.6;
            color: #666666;
        }
        a {
            color: var(--primary-accent);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        a:hover {
            color: var(--secondary-accent);
            text-decoration: underline;
        }
        .section-nav {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
        }
        .nav-button {
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            font-size: 1.1em;
            font-weight: 500;
            color: #fff;
            background-color: var(--primary-accent);
            border-radius: 8px;
            text-decoration: none;
            transition: background-color 0.3s, transform 0.2s;
            cursor: pointer;
        }
        .nav-button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        .card {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px var(--shadow-color);
            transition: transform 0.3s, box-shadow 0.3s, background-color 0.3s;
            margin-bottom: 25px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            border: 1px solid var(--border-color);
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.15);
            background-color: var(--card-hover-bg);
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }
        .card img {
            width: 80px;
            height: 80px;
            border-radius: 10px;
            margin-bottom: 15px;
            transition: transform 0.3s;
        }
        .card img:hover {
            transform: scale(1.05);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .metric-card {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px var(--shadow-color);
            text-align: center;
            border-left: 4px solid var(--primary-accent);
            transition: transform 0.3s, box-shadow 0.3s;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 180px;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-accent);
        }
        .metric-label {
            display: block;
            font-size: 0.9rem;
            color: #999999;
            margin-top: 5px;
        }
        .progress-circle {
            position: relative;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: conic-gradient(
                var(--primary-accent) 0deg, 
                var(--primary-accent) 0deg,
                var(--border-color) 0deg
            );
            transition: background 1s ease-in-out;
            margin-bottom: 10px;
        }
        .progress-circle::before {
            content: '';
            position: absolute;
            background: #ffffff;
            border-radius: 50%;
            width: 90px;
            height: 90px;
        }
        .progress-circle .value-text {
            position: relative;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-color);
        }
    </style>
"""

def get_circle_style(percent, accent_color_low, accent_color_med, accent_color_high):
    color = accent_color_low
    if percent > 50:
        color = accent_color_med
    if percent > 80:
        color = accent_color_high
    return f"""
        <div class="progress-circle" style="background: conic-gradient(
            {color} 0deg, 
            {color} {3.6 * percent}deg,
            var(--border-color) {3.6 * percent}deg
        );">
            <span class="value-text">{percent}%</span>
        </div>
    """

class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global request_count, last_request_time

        request_count += 1
        last_request_time = time.time()

        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        uptime = time.time() - start_time
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        # Update Prometheus metrics
        cpu_gauge.set(cpu)
        mem_gauge.set(mem)
        uptime_gauge.set(uptime)
        requests_counter.inc()

        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
        last_req_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_request_time))

        if self.path in ['/', '/index.html']:
            self.show_tools()
        elif self.path == '/projects':
            self.show_projects()
        elif self.path == '/appinfo':
            self.show_app_info(cpu, mem, uptime_str, last_req_str, disk, net)
        elif self.path == '/metrics':
            self.serve_metrics()
        else:
            self.send_error(404, "Page Not Found")

    def show_tools(self):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🚀 DevOps Hub</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <h1>DevOps Hub</h1>
                <div class="card-grid">
                    <div class="card">
                        <a href="https://www.docker.com" target="_blank">
                            <img src="https://www.docker.com/wp-content/uploads/2022/03/vertical-logo-monochromatic.png" alt="Docker Logo">
                        </a>
                        <h3>Docker</h3>
                        <p>Simplifies packaging and running applications in isolated containers.</p>
                    </div>
                    <div class="card">
                        <a href="https://kubernetes.io" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg" alt="Kubernetes Logo">
                        </a>
                        <h3>Kubernetes</h3>
                        <p>Container orchestration platform for scaling and managing containerized apps.</p>
                    </div>
                    <div class="card">
                        <a href="https://www.jenkins.io" target="_blank">
                            <img src="https://www.jenkins.io/images/logos/jenkins/jenkins.png" alt="Jenkins Logo">
                        </a>
                        <h3>Jenkins</h3>
                        <p>Automates building, testing, and deployment (CI/CD pipelines).</p>
                    </div>
                    <div class="card">
                        <a href="https://prometheus.io" target="_blank">
                            <img src="https://prometheus.io/_next/static/media/prometheus-logo.7aa022e5.svg" alt="Prometheus Logo">
                        </a>
                        <h3>Prometheus</h3>
                        <p>Time-series monitoring and alerting toolkit for microservices.</p>
                    </div>
                    <div class="card">
                        <a href="https://grafana.com" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a1/Grafana_logo.svg" alt="Grafana Logo">
                        </a>
                        <h3>Grafana</h3>
                        <p>Visualization and analytics platform for interactive dashboards.</p>
                    </div>
                    <div class="card">
                        <a href="https://www.terraform.io" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/Terraform_Logo.svg" alt="Terraform Logo">
                        </a>
                        <h3>Terraform</h3>
                        <p>Infrastructure as code tool to provision and manage cloud resources.</p>
                    </div>
                </div>
                <div class="section-nav">
                    <a href="/projects" class="nav-button">Real-World Projects</a>
                    <a href="/appinfo" class="nav-button">View App Metrics</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.respond(html_content)

    def show_projects(self):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Companies & Projects</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <h1>Real-World DevOps Projects</h1>
                <div class="card-grid">
                    <div class="card">
                        <a href="https://jobs.netflix.com/teams/devops" target="_blank">
                           <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" alt="Netflix">
                        </a>
                        <h3>Netflix</h3>
                        <p>Leading in microservices and chaos engineering for global streaming scale.</p>
                    </div>
                    <div class="card">
                        <a href="https://aws.amazon.com/devops" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon">
                        </a>
                        <h3>Amazon</h3>
                        <p>Deploying code every few seconds, enabling rapid innovation worldwide.</p>
                    </div>
                    <div class="card">
                        <a href="https://www.spotify.com/us/jobs/" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" alt="Spotify">
                        </a>
                        <h3>Spotify</h3>
                        <p>Empowering teams with fast, independent feature releases to millions.</p>
                    </div>
                    <div class="card">
                        <a href="https://www.facebook.com/careers" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg" alt="Facebook">
                        </a>
                        <h3>Facebook</h3>
                        <p>Rolling out new features daily to billions of users with strong CI/CD pipelines.</p>
                    </div>
                    <div class="card">
                        <a href="https://medium.com/airbnb-engineering/tagged/devops" target="_blank">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_Bélo.svg" alt="Airbnb">
                        </a>
                        <h3>Airbnb</h3>
                        <p>Scaling globally using containers and automated deployments for fast delivery.</p>
                    </div>
                </div>
                <div class="section-nav">
                    <a href="/" class="nav-button">Tools Dashboard</a>
                    <a href="/appinfo" class="nav-button">View App Metrics</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.respond(html_content)


    def show_app_info(self, cpu, mem, uptime_str, last_req_str, disk, net):
        # Using a simple color-coded system for the circular charts
        green = "#2ecc71"
        yellow = "#f1c40f"
        red = "#e74c3c"
        
        cpu_circle = get_circle_style(cpu, green, yellow, red)
        mem_circle = get_circle_style(mem, green, yellow, red)
        disk_circle = get_circle_style(disk.percent, green, yellow, red)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>App Metrics</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <h1>Application & System Metrics</h1>
                <div class="metrics-grid">
                    <div class="metric-card">
                        {cpu_circle}
                        <span class="metric-label">CPU Usage</span>
                    </div>
                    <div class="metric-card">
                        {mem_circle}
                        <span class="metric-label">Memory Usage</span>
                    </div>
                    <div class="metric-card">
                        {disk_circle}
                        <span class="metric-label">Disk Usage</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{net.bytes_sent // (1024**2)} MB</div>
                        <span class="metric-label">Network Sent</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{net.bytes_recv // (1024**2)} MB</div>
                        <span class="metric-label">Network Received</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{uptime_str}</div>
                        <span class="metric-label">App Uptime</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{last_req_str}</div>
                        <span class="metric-label">Last Request</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{request_count}</div>
                        <span class="metric-label">Total Requests</span>
                    </div>
                </div>
                <div class="section-nav">
                    <a href="/" class="nav-button">Tools Dashboard</a>
                    <a href="/projects" class="nav-button">Project Showcase</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.respond(html_content)

    def serve_metrics(self):
        metrics_page = generate_latest(registry)
        self.send_response(200)
        self.send_header("Content-type", CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(metrics_page)

    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

if __name__ == "__main__":
    print(f"Starting server at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), MetricsHandler) as httpd:
        httpd.serve_forever()
