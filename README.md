# Elite Entity Tracker Dashboard

## Render Deployment Guide
1. Create a Web Service instance on Render connected to your project repository.
2. Select **Python** as your Runtime environment.
3. Configure the **Build Command**: `pip install -r requirements.txt`
4. Configure the **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
