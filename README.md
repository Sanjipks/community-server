# Community Server

This is a FastAPI-based application for managing community posts, categories, jokes, and chat functionality.

## Prerequisites

- Python 3.9 or later
- MongoDB (running locally or in the cloud)

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/community-server.git
   cd community-server

   ```

2. Create Virtual Environment
   => python3 -m venv venv

3. to run the application it needs two steps;

i. Activate Virtual Environment
=> "source venv/bin/activate"
ii.Run the Application with Uvicorn
=> "uvicorn app.main:app --reload"
