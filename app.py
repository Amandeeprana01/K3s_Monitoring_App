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
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #f0f0f5;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.12);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(31,38,135,0.37);
            backdrop-filter: blur(8.5px);
            -webkit-backdrop-filter: blur(8.5px);
            border: 1px solid rgba(255,255,255,0.18);
            max-width: 900px;
            margin: 20px auto;
        }
        h1, h2 {
            color: #ffd86b;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        p {
            font-size: 17px;
            line-height: 1.7;
            color: #e8e8ffcc;
        }
        a {
            color: #81a1ff;
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
            color: #c7d3ff;
        }
    </style>
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
            <title>🚀 Top DevOps Tools</title>
            {STYLE}
            <style>
                .tool-block {{
                    overflow: auto;
                    margin-bottom: 25px;
                    padding: 10px;
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 10px;
                }}
                .tool-block img {{
                    width: 150px;
                    float: left;
                    margin-right: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
                    background: rgba(255, 255, 255, 0.3);
                    padding: 5px;
                }}
                .label {{
                    font-weight: 700;
                    color: #ffeb99;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1><b>Top DevOps Tools & Market Trends</b></h1>

                <div class="tool-block">
                    <img src="https://www.docker.com/wp-content/uploads/2022/03/vertical-logo-monochromatic.png" alt="Docker Logo">
                    <h2><b>Docker</b></h2>
                    <p><span class="label">Description:</span> Simplifies packaging and running applications in isolated containers.</p>
                    <p><span class="label">Market Share:</span> Used by 70% of global organizations.</p>
                </div>

                <div class="tool-block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg" alt="Kubernetes Logo">
                    <h2><b>Kubernetes</b></h2>
                    <p><span class="label">Description:</span> Container orchestration platform for scaling and managing containerized apps.</p>
                    <p><span class="label">Market Share:</span> Adopted by 80% of enterprises worldwide.</p>
                </div>

                <div class="tool-block">
                    <img src="https://www.jenkins.io/images/logos/jenkins/jenkins.png" alt="Jenkins Logo">
                    <h2><b>Jenkins</b></h2>
                    <p><span class="label">Description:</span> Automates building, testing, and deployment (CI/CD pipelines).</p>
                    <p><span class="label">Market Share:</span> Around 60% adoption for CI/CD pipelines.</p>
                </div>

                <div class="tool-block">
                    <img src="https://prometheus.io/_next/static/media/prometheus-logo.7aa022e5.svg" alt="Prometheus Logo">
                    <h2><b>Prometheus</b></h2>
                    <p><span class="label">Description:</span> Time-series monitoring and alerting toolkit for microservices.</p>
                    <p><span class="label">Market Share:</span> Dominant choice for microservices monitoring.</p>
                </div>

                <div class="tool-block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a1/Grafana_logo.svg" alt="Grafana Logo">
                    <h2><b>Grafana</b></h2>
                    <p><span class="label">Description:</span> Visualization and analytics platform to create interactive dashboards.</p>
                    <p><span class="label">Market Share:</span> Widely used alongside Prometheus for metrics visualization.</p>
                </div>

                <div class="tool-block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/Terraform_Logo.svg" alt="Terraform Logo">
                    <h2><b>Terraform</b></h2>
                    <p><span class="label">Description:</span> Infrastructure as code tool to provision and manage cloud resources.</p>
                    <p><span class="label">Market Share:</span> Over 50% of DevOps teams worldwide.</p>
                </div>

                <p style="text-align:center; margin-top:30px;">
                    <a href="/projects">See Real-World Projects</a> | 
                    <a href="/appinfo">View App Metrics</a>
                </p>
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
            <title>Company Real-World Projects & Use Cases</title>
            {STYLE}
            <style>
                .block {{
                    background: rgba(255, 255, 255, 0.08);
                    padding: 20px;
                    margin-bottom: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    text-align: center;
                    transition: transform 0.3s;
                }}
                .block:hover {{
                    transform: scale(1.02);
                }}
                .block img {{
                    width: 80px;
                    margin-bottom: 10px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.2);
                    padding: 5px;
                }}
                h3 {{
                    color: #ffd86b;
                    margin-top: 10px;
                }}
                p {{
                    color: #e8e8ffcc;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1><b>Company Real-World Projects</b></h1>

                <div class="block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" alt="Netflix">
                    <h3>Netflix</h3>
                    <p>Leading in microservices and chaos engineering for global streaming scale.</p>
                </div>

                <div class="block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon">
                    <h3>Amazon</h3>
                    <p>Deploying code every few seconds, enabling rapid innovation worldwide.</p>
                </div>

                <div class="block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" alt="Spotify">
                    <h3>Spotify</h3>
                    <p>Empowering squads with fast, independent feature releases to millions.</p>
                </div>

                <div class="block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg" alt="Facebook">
                    <h3>Facebook</h3>
                    <p>Rolling out new features daily to billions of users with strong CI/CD pipelines.</p>
                </div>

                <div class="block">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_Bélo.svg" alt="Airbnb">
                    <h3>Airbnb</h3>
                    <p>Scaling globally using containers and automated deployments for fast delivery.</p>
                </div>

                <h1 style="margin-top:50px;"><b>Popular DevOps Project Types</b></h1>

                <div class="block">
                    <h3>Microservices Migration</h3>
                    <p>Breaking monoliths into scalable, independent services.</p>
                </div>

                <div class="block">
                    <h3>Continuous Deployment</h3>
                    <p>Automating builds, tests, and releases for faster delivery.</p>
                </div>

                <div class="block">
                    <h3>Multi-Cloud Deployments</h3>
                    <p>Ensuring flexibility and resilience across multiple clouds.</p>
                </div>

                <p style="text-align:center; margin-top:30px;">
                    <a href="/">Top Dev Tools</a> | 
                    <a href="/appinfo">View App Metrics </a>
                </p>
            </div>
        </body>
        </html>
        """
        self.respond(html_content)

    def show_app_info(self, cpu, mem, uptime_str, last_req_str, disk, net):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>App & System Information</title>
            {STYLE}
        </head>
        <body>
            <div class="container">
                <h1><b>Application & System Metrics</b></h1>
                <p><span class="label">CPU Usage:</span> {cpu}%</p>
                <p><span class="label">Memory Usage:</span> {mem}%</p>
                <p><span class="label">Disk Usage:</span> {disk.percent}% ({disk.used // (1024**3)} GB used of {disk.total // (1024**3)} GB)</p>
                <p><span class="label">Network Sent:</span> {net.bytes_sent // (1024**2)} MB</p>
                <p><span class="label">Network Received:</span> {net.bytes_recv // (1024**2)} MB</p>
                <p><span class="label">App Uptime:</span> {uptime_str}</p>
                <p><span class="label">Last Request:</span> {last_req_str}</p>
                <p><span class="label">Request Count:</span> {request_count}</p>
                <p style="text-align:center; margin-top:30px;">
                    <a href="/">← Top Tools</a> | 
                    <a href="/projects">Project Showcase </a>
                </p>
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

