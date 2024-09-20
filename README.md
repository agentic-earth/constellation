# 🌌 Constellation API

![Constellation Banner](https://your-image-url.com/banner.png)

Welcome to the **Constellation API**! 🚀 A robust and scalable FastAPI application designed to manage **pipelines**, **blocks**, **edges**, and **audit logs** with advanced search capabilities. Leveraging the power of **Supabase** for efficient data management and querying, this API ensures seamless orchestration and comprehensive monitoring of your data workflows.

## 📚 Table of Contents

- [🌟 Features](#-features)
- [🛠️ Technologies Used](#️-technologies-used)
- [🚀 Getting Started](#-getting-started)
  - [⚙️ Prerequisites](#️-prerequisites)
  - [🔧 Installation](#-installation)
- [🖥️ Running the Application](#️-running-the-application)
- [🔍 API Documentation](#-api-documentation)
- [📈 Search Functionality](#-search-functionality)
- [📝 Contributing](#-contributing)
- [📜 License](#-license)
- [📞 Contact](#-contact)

## 🌟 Features

- **CRUD Operations**: Comprehensive Create, Read, Update, and Delete functionalities for pipelines, blocks, edges, and audit logs.
- **Advanced Search**: Powerful search capabilities based on various taxonomies and classifications.
- **Graph Data Structures**: Manage complex relationships between blocks and edges effectively.
- **Audit Logging**: Maintain a detailed audit trail for all critical operations, enhancing accountability and traceability.
- **Scalable Architecture**: Built with a modular **Routes → Controllers → Services** structure for easy maintenance and scalability.
- **Robust Logging**: Utilizes `ConstellationLogger` for consistent and detailed logging across all operations.

## 🛠️ Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) 🚀 - A modern, fast (high-performance) web framework for building APIs with Python.
- [Uvicorn](https://www.uvicorn.org/) 🐍 - A lightning-fast ASGI server implementation, using uvloop and httptools.
- [Supabase](https://supabase.com/) ☁️ - An open-source Firebase alternative for backend services.
- [Pydantic](https://pydantic-docs.helpmanual.io/) 📄 - Data validation and settings management using Python type annotations.
- [Python 3.8+](https://www.python.org/) 🐍 - The programming language used for developing the API.

## 🚀 Getting Started

### ⚙️ Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+** installed on your machine. You can download it [here](https://www.python.org/downloads/).
- **Supabase Account**: Sign up for a free account at [Supabase](https://supabase.com/) and set up your database.
- **Git** installed for version control. Download it [here](https://git-scm.com/downloads).

### 🔧 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/constellation-api.git
   cd constellation-api
   ```

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory and add your Supabase credentials and other configurations.

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

   Ensure that the `.env` file is added to `.gitignore` to keep your credentials secure.

## 🖥️ Running the Application

To launch the API locally on port 8081, run the following command:

```bash
python main.py
```

Default Endpoints
Root Endpoint:
GET /
Returns a welcome message.

Health Check:
GET /health
Checks the health status of the API.

🔍 API Documentation
FastAPI provides interactive API documentation out of the box. Once the application is running, you can access it here:

Swagger UI: http://localhost:8081/docs
ReDoc: http://localhost:8081/redoc
Explore all available endpoints, their request and response schemas, and interact with the API directly from the browser.

📈 Search Functionality
One of the standout features of the Constellation API is its advanced search capabilities. You can search through blocks and edges based on different taxonomies and classifications. Here's how to utilize the search endpoints:

Search Blocks
Endpoint: GET /blocks/search/
Query Parameters:
name (Optional): Filter blocks by name.
block_type (Optional): Filter blocks by type (e.g., dataset, model).
taxonomy (Optional): Filter blocks by taxonomy categories.
Example Request:

```bash
GET http://localhost:8081/blocks/search/?name=DataProcessor&block_type=model&taxonomy=category1&taxonomy=category2
```
Search Edges
Endpoint: GET /edges/search/
Query Parameters:
name (Optional): Filter edges by name.
taxonomy (Optional): Filter edges by taxonomy categories.
Example Request:

```bash
GET http://localhost:8081/edges/search/?name=EdgeConnector&taxonomy=category1
```
Note: Ensure that the taxonomy categories you provide match the existing categories in your database.
