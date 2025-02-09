# Tetris vs AI in Streamlit

This repository contains a minimal Streamlit application that runs two instances of a Tetris game side by side: one for a human player (controlled via buttons) and one controlled by a simple AI. The goal is to see who can achieve a higher score or survive longer!

## How it Works

- **User Board (Left):** Controlled via Streamlit buttons (move left, move right, rotate, soft drop, hard drop).
- **AI Board (Right):** Automatically calculates a “best” placement for each falling Tetris piece based on a simple heuristic.
- The games drop their pieces every ~0.5 seconds.  
- Once one board reaches `game_over`, the winner is declared.

## Files

- **app.py**: The main Streamlit application script. All Tetris logic, AI routine, and rendering code are contained in this single file.
- **requirements.txt**: Lists Python dependencies (Streamlit + Pygame).
- **README.md**: This file, describing how to run and deploy the app.

## Running Locally

1. Create and activate a virtual environment (optional but recommended).
2. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
4. Open your browser at the indicated local URL.

## Deploying on Streamlit Cloud

1. Push this repo to GitHub.  
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and click **New app**.
3. Select your GitHub repository, branch, and `app.py` as the entry point.
4. Deploy! You should see your Tetris vs AI app live on Streamlit Cloud.

## Caveats

- Real-time keyboard handling in a web app can be challenging. Here we use simple button clicks to capture user moves.
- The “frame rate” is not truly real-time. Each move triggers a re-run, and there is a 0.5-second pause for the AI step. Adjust as desired.

Enjoy playing against the AI!
