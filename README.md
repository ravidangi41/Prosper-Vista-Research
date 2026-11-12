🚀 Prosper Vista Research

Financial Market Research & Precious Metals Dashboard

A responsive financial research website built and deployed using Google Cloud Platform, Docker, Docker Compose, FastAPI, MySQL and Nginx.

🌐 Live Website: http://35.225.167.19:8082/markets
💻 GitHub Repository: https://github.com/ravidangi41/Prosper-Vista-Research

---

📌 Project Overview

Prosper Vista Research is a financial market research website focused on precious metals, including MCX Gold, MCX Silver, XAUUSD and XAGUSD.

The project demonstrates how to build, containerize and deploy a web application on a Google Cloud virtual machine using Docker and related DevOps technologies.

✨ Key Features

- MCX Gold and Silver market snapshot
- Global Gold (XAUUSD) and Silver (XAGUSD) reference prices
- Market trend chart preview
- Financial research and market insights sections
- Admin login foundation
- Manual price update capability
- Live price API integration foundation
- MySQL database integration
- Responsive web interface

🛠️ Technology Stack

Technology| Purpose
Google Cloud Platform| Cloud hosting
Ubuntu Linux| Server operating system
Docker| Application containerization
Docker Compose| Multi-container management
FastAPI| Backend framework
Python| Application development
MySQL| Database
Nginx| Web server / reverse proxy
Git & GitHub| Version control

🏗️ Project Architecture

              Users
                |
                v
       Google Cloud VM
          Ubuntu Linux
                |
                v
          Docker Compose
           /         \
          v           v
      FastAPI       MySQL
       Backend     Database
          |
          v
    Financial Dashboard

🚀 Deployment Steps

1. Clone the Repository

git clone https://github.com/ravidangi41/Prosper-Vista-Research.git
cd Prosper-Vista-Research

2. Configure Environment

Copy the example environment file:

cp .env.example .env

Update the required passwords, secret key and admin configuration in ".env".

Never upload your actual ".env" file or credentials to GitHub.

3. Build and Start Containers

docker compose up -d --build

4. Check Running Containers

docker compose ps

5. View Application Logs

docker compose logs -f

6. Access the Website

Open the configured public IP and application port in your browser.

📚 DevOps Skills Demonstrated

- Linux server administration
- Docker image building
- Docker container management
- Docker Compose orchestration
- Environment variable configuration
- MySQL container integration
- Google Cloud VM deployment
- Firewall and network connectivity
- GitHub repository management
- Application troubleshooting

🔐 Security Notes

- Keep database credentials private.
- Use strong admin passwords.
- Store secrets in environment variables.
- Configure HTTPS before production use.
- Restrict administrative access appropriately.

📊 Market Data Disclaimer

Initial market values and sample chart data are illustrative. Genuine real-time market prices require an authorized market-data provider and applicable exchange permissions. This website is a learning and research project, not investment advice.

👨‍💻 Project Author

Ravi
Cloud & DevOps Learner | Financial Market Research

GitHub: https://github.com/ravidangi41

---

⭐ If you find this project useful, feel free to explore the repository and share your feedback.

Learning by Building. Building by Deploying.
