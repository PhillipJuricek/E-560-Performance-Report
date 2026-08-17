# E-560 M-Exchanger Performance Report
<img width="2680" height="1244" alt="image" src="https://github.com/user-attachments/assets/2c40c5d6-51cf-4433-8d75-956e9f1cc750" />
<img width="1460" height="481" alt="image" src="https://github.com/user-attachments/assets/df6fda19-4337-402c-a1a5-7f980c424568" />
<img width="1460" height="481" alt="image" src="https://github.com/user-attachments/assets/fab54197-65e8-4cde-8506-06273aed73cf" />
<img width="1460" height="477" alt="image" src="https://github.com/user-attachments/assets/4afff76c-124d-473d-8be6-cf521adeb1aa" />
<img width="2710" height="1398" alt="image" src="https://github.com/user-attachments/assets/b9f3a043-ce44-4303-9473-d5644871e8ac" />
<img width="2678" height="1408" alt="image" src="https://github.com/user-attachments/assets/99709a80-2ff4-480e-a447-7fb88d3ea48c" />
<img width="2658" height="562" alt="image" src="https://github.com/user-attachments/assets/3332fd08-f4dd-40ef-983e-2f1c4f5ffc2e" />


A Streamlit app that turns two source files into an exchanger fleet performance
report:

- **SCADA Process Data (CSV)** — pulled from the South Battery section
  (e.g. `E-560-180-Aug3.CSV`)
- **Event Logbook Data (XLSX)** — the operator's native cleaning log
  (e.g. `2026 - E560 & 5611 Cleaning Log July 26.xlsx`)

You upload both files in the app and it generates fleet-wide RNTP / RRI plots,
a per-exchanger current-vs-previous cycle comparison, worst-performer metrics,
and a full methodology section.

---

## Windows — setup (one time only)

1. **Install Python 3.13** from <https://www.python.org/downloads/>.
   - During install, tick **"Add python.exe to PATH"**.
   - If you get both "Install now" and "Customize installation", either is fine.

2. **Open PowerShell** in this folder:
   - In File Explorer, click into the `E-560` folder.
   - Hold `Shift`, right-click empty space, choose **"Open PowerShell window here"** (or use the `run.bat` launcher and skip the rest of this section).

3. **Create a virtual environment** (isolated, so it never touches your system Python):

   ```
   py -3.13 -m venv .venv
   .\.venv\Scripts\activate
   ```

   (You should see `(.venv)` at the start of your prompt.)

4. **Install the pinned dependencies**:

   ```
   pip install -r requirements.txt
   ```

## Windows — run the app

Make sure the venv is active (step 3 above), then:

```
streamlit run app_streamlit.py
```

Your browser will open automatically at `http://localhost:8501`.

### Easier: use the one-click launcher

Double-click **`run.bat`**. It does everything for you — creates the venv and
installs dependencies on first run, then launches the app.

---

## macOS — setup and run

The same steps, but with the macOS commands:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_streamlit.py
```

---

## Using the app

1. Drag the **SCADA CSV** into the left upload box.
2. Drag the **event logbook XLSX** into the right upload box.
3. The report renders below. Use the **Select Exchanger** dropdown to switch
   between the per-exchanger cycle comparison plots.

---

## Project layout

| File / folder      | Purpose                                                          |
| ------------------ | ---------------------------------------------------------------- |
| `app_streamlit.py` | The Streamlit app (entry point)                                  |
| `app.py`           | Optional command-line version of the same analysis               |
| `config.py`        | Exchangers, colors, and analysis parameters                       |
| `analysis/`        | Data loading, metrics, rankings, cycle detection                  |
| `visualization/`   | Plot generation (fleet + cycle comparison)                       |
| `methodology.py`   | Written methodology sections shown in the app                    |
| `data/`            | Sample source files                                              |
| `requirements.txt` | Pinned, verified dependency list                                 |
| `run.bat`          | One-click Windows launcher                                       |

## Configuration

Analysis parameters (rolling window, minimum flow, state deadband) and the
exchanger list all live in `config.py` and can be tuned without touching the
analysis code.

## Troubleshooting (Windows)

- **`'pip' is not recognized`** — the venv isn't active, or Python wasn't added
  to PATH. Use `py -3.13 -m venv .venv` and `.\.venv\Scripts\activate` again,
  or just double-click `run.bat`.
- **Corporate proxy blocks `pip install`** — tell IT the app needs
  `pypi.org` access, or set the proxy in the command:
  `pip install --proxy http://your-proxy:port -r requirements.txt`
- **`streamlit` command not found** — the venv isn't active.
- **"Port 8501 is already in use"** — something else is on that port. Run
  `streamlit run app_streamlit.py --server.port 8502`.
- **The app opens but plots look different** — font/DPI differences between
  machines are expected and cosmetic; the data is identical.
