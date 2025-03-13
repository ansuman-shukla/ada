# Ada - Your Personal Assistant

Ada is an AI-powered personal assistant designed to streamline your daily life by helping you manage tasks, store and retrieve personal memories, and search the web for information. Built with a modern tech stack, Ada combines a user-friendly Streamlit interface with advanced natural language processing capabilities powered by the Gemini AI model.

## Features

- **Task Management**: Create, view, update, and delete tasks with priorities and schedules
- **Memory Storage**: Store and retrieve personal information securely
- **Web Search**: Find information from the internet in real-time

## Running the Application

### Prerequisites

- **Python**: Version 3.11 or later
- **API Keys**:
  - Google Serper API key (for web search)
  - Gemini AI API key (for language processing)
  - Pinecone API key (for vector storage)
- **MongoDB**: A running MongoDB instance (local or cloud-based, e.g., MongoDB Atlas)
- **Git**: For cloning the repository

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ansuman-shukla/ada.git
   cd ada
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   SERPER_API_KEY=your_serper_api_key
   uri=your_mongodb_connection_string
   ```
   Replace the placeholders with your actual API keys and MongoDB connection string.

5. **Verify MongoDB Connection**:
   Ensure your MongoDB instance is running. The application will automatically create a tasks database and collection when you start using it.

6. **Start the Streamlit Frontend**:
   ```bash
   streamlit run app.py
   ```
   This launches the main application at http://localhost:8501 (default port).

7. **Interact with Ada**:
   - Open your browser to the provided URL and start chatting with Ada
   - The sidebar provides a handy guide to Ada's capabilities and example commands

## Example Interactions

### Task Management

#### View All Tasks:
- You: "Show me all my tasks"
- Ada: Displays a bulleted list of all tasks stored in the database

#### Create a Task:
- You: "Add a task: Name: Buy groceries, Description: Milk and eggs, Status: pending, Date: 17:10:2023, Time: 10:00:00, Priority: medium"
- Ada: "Task 'Buy groceries' has been created for 17:10:2023 at 10:00:00."

#### View Tasks by Date:
- You: "Can you get me all tasks for 15:10:2023?"
- Ada: Lists all tasks scheduled for October 15, 2023

#### Update a Task:
- You: "Update my task on 17:10:2023 at 10:00:00 to Time: 11:00:00, Priority: high"
- Ada: Updates the task and confirms the changes

#### Delete a Task:
- You: "Delete my task on 17:10:2023 at 10:00:00"
- Ada: "Task deleted"

### Memory Management

#### Store a Memory:
- You: "Remember that my passport number is 123456789"
- Ada: "I've stored that your passport number is 123456789."

#### Retrieve a Memory:
- You: "What is my passport number?"
- Ada: "Your passport number is 123456789."

### Web Search

#### Search the Web:
- You: "What's the capital of France?"
- Ada: "The capital of France is Paris."
- You: "What's the weather like today?"
- Ada: Provides a summary based on web search results

## Important Notes

- **Date and Time Format**:
  - Use dd:mm:yyyy for dates (e.g., 15:10:2023)
  - Use hh:mm:ss in 24-hour format for times (e.g., 14:00:00)

- **Task Creation**:
  - When creating or updating tasks, include all required fields: Name, Description, Status (e.g., pending, in progress, completed), Date, Time, and Priority (e.g., high, medium, low).

- **Memory Storage**:
  - Explicitly instruct Ada to store information with phrases like "Remember that..." or "Store this information...". She'll save it in the vector database for later retrieval.

- **Web Search**:
  - Ada uses the Google Serper API to fetch real-time information from the web, perfect for current events or quick facts.
