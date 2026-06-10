# 😈 Save the Tasmanian Devil: Disease & Genetic Tracker

An interactive, research-grade conservation console built with **Streamlit** and a dual-mode database engine (**MySQL & serverless SQLite**). This tracker monitors the spread of Devil Facial Tumor Disease (DFTD) and recommends optimal breeding pairs to prevent inbreeding depression and maintain immune diversity across Tasmanian sanctuaries.

📊 **Live Demo**: [tasmanian-devil-tracker.streamlit.app](https://tasmanian-devil-tracker-o79hhont7e7lqfzjwk2gnc.streamlit.app/)

---

## 🔬 The Conservation Challenge
The Tasmanian Devil (*Sarcophilus harrisii*) is facing extinction in the wild due to **Devil Facial Tumor Disease (DFTD)**—a transmissible, clonal, cell-line cancer spread through social biting. DFTD has two primary strains: **DFT1** (statewide since 1996) and **DFT2** (geographically localized to the Channel region since 2014).

Because devils have extremely low genetic diversity—specifically at the **Major Histocompatibility Complex (MHC)** loci—their immune systems fail to recognize tumor cells as foreign, leading to 100% mortality within 6–12 months of infection. 

To save the species, conservationists manage "insurance populations" in disease-free captive sanctuaries. This console is designed to help wildlife managers evaluate breeding pairs, track outbreak intervals, and rank candidates for re-introduction into the wild.

---

## ⚡ Core Features

### 1. 🗺️ Metapopulation & Sanctuary Map
- Maps coordinates of all 10 major sanctuaries and reserves in Tasmania.
- Visually sizes markers by devil population density.
- Color-codes locations by disease severity (Green for clean zones, Amber for low-prevalence, Red for critical outbreak zones).

### 2. 🧬 Breeding Lineage & MHC Complement Assessor
- **Kinship Coefficient**: Uses a **Recursive SQL CTE** to walk back 3 generations, identify shared ancestors, and compute inbreeding risks.
- **MHC Diversity Check**: Evaluates candidate haplotypes (alleles `Saha-I*01` through `Saha-I*06`) to ensure the offspring inherits complementary immune genes, maximizing disease resilience.
- **Pedigree Visualizer**: Renders a dark-themed visual HTML/CSS lineage tree of the breeding pair and their ancestors.

### 3. 📈 Outbreak Surveillance Monitor
- Uses SQL window functions (`LAG()`) to calculate the time difference (in days) between consecutive positive cases in each region, alerting researchers if the transmission interval is rapidly shrinking (accelerating outbreaks).
- Features a clinical chart analyzing average bite scars (the primary vector for DFTD) across health groups.

### 4. 🛡️ Sanctuary Biosecurity Transfer Guard
- A native database trigger (`BEFORE UPDATE`) that intercept updates. If a researcher attempts to transfer an infected or symptomatic devil into a sanctuary marked as a `is_clean_zone` (like Maria Island), the database engine aborts the transaction and throws a biosecurity exception.

### 5. 😈 Individual Profile & Clinical Timeline
- Search any devil by ID or Name to view their demographics, pedigree, and health logs.
- Displays a Matplotlib **Weight Trajectory Chart** comparing the individual's weight against a healthy reference curve to detect clinical wasting (cachexia).
- Renders a clean vertical timeline of clinical field logs and diagnostic notes.

---

## 🗄️ Database Architecture

The system runs on 4 relational tables:
- **`sanctuaries`**: Tracks capacities, postcodes, and biosecurity status.
- **`strains`**: DFTD variants (Healthy, DFT1, DFT2).
- **`devils`**: Pedigree links (`mother_id`, `father_id`), demographics, and MHC alleles.
- **`health_logs`**: Chronological weights, bite scars, PCR outcomes, and clinical notes.

---

## 🚀 Local Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Dhimanhdg/Tasmanian-Devil-Tracker.git
   cd Tasmanian-Devil-Tracker
   ```
2. Set up the virtual environment and install packages:
   ```bash
   .venv\Scripts\pip install -r requirements.txt
   ```
3. Run the SQLite data generator to populate ~75,000 research rows:
   ```bash
   $env:USE_SQLITE="true"
   .venv\Scripts\python data_factory.py
   ```
4. Start the Streamlit application:
   ```bash
   .venv\Scripts\streamlit run app.py
   ```

---

## ☁️ Serverless Free Cloud Deployment (Streamlit Cloud)

This app is configured to run serverlessly in **SQLite Mode** for 100% free cloud hosting:
1. Push this repository to your GitHub account.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and connect your repository.
3. Click **Advanced Settings** before deploying and add the following environment variable under the **Secrets** section:
   ```toml
   USE_SQLITE = "true"
   ```
4. Click **Deploy!**
